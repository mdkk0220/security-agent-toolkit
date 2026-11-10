from approvals import hold_for_approval
from audit import log_line
from enrichment import enrich_incident
from incident import change_status, match_playbooks
from retry_runner import MAX_TRIES, run_with_retry
from routing import apply_route, decide_route

VIP_REVIEW_ACTIONS = ["담당자 알림", "티켓 생성"]


def run_playbook_with_retry(incident, playbook, state, action_log, fail_plan):
    incident["playbook"] = playbook["id"]
    change_status(incident, "분류됨")
    failed = False
    for action in playbook["actions"]:
        result = run_with_retry(action, incident, state, fail_plan, MAX_TRIES)
        if result.startswith("실패"):
            failed = True
        action_log.append(log_line(incident, action, result))
    if failed:
        return "일부 실패"
    change_status(incident, "조치됨")
    return "실행 완료"


def run_day_flow(
    incidents,
    registry,
    users_info,
    source_ips,
    trusted_ips,
    state,
    action_log,
    fail_plan,
):
    pending = []
    route_log = []
    for incident in incidents:
        enrich_incident(incident, users_info, source_ips, trusted_ips)
        route, reason = decide_route(incident)
        apply_route(incident, route, reason, route_log)
        result_text = "맞는 플레이북 없음"
        if route == "오탐 종료":
            result_text = "오탐 종료"
        elif route == "승인 필요":
            pending.append(
                hold_for_approval(
                    incident,
                    "VIP 확인",
                    VIP_REVIEW_ACTIONS,
                    "VIP 계정이라 경로가 승인 필요",
                    action_log,
                )
            )
            result_text = "승인 대기"
        else:
            for playbook in match_playbooks(incident, registry):
                if playbook["approval"] != "자동":
                    pending.append(
                        hold_for_approval(
                            incident,
                            playbook["id"],
                            playbook["actions"],
                            "플레이북 승인 값이 " + playbook["approval"],
                            action_log,
                        )
                    )
                    result_text = "승인 대기"
                else:
                    result_text = run_playbook_with_retry(
                        incident, playbook, state, action_log, fail_plan
                    )
        print(
            incident["id"],
            incident["entity"],
            "->",
            result_text,
            "(상태: " + incident["status"] + ")",
        )
    return pending
