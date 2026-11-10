from audit import log_line
from incident import change_status, run_action

APPROVERS = ["kim.sec", "lee.soc"]


def hold_for_approval(incident, playbook_id, actions, why, action_log):
    incident["playbook"] = playbook_id
    incident["actions"] = actions
    incident["why"] = why
    change_status(incident, "분류됨")
    action_log.append(log_line(incident, "전체", "승인 대기 — " + why))
    return incident


def is_authorized(approver):
    return approver in APPROVERS


def execute_actions(item, state, action_log, approver):
    for action in item["actions"]:
        result = run_action(action, item, state)
        action_log.append(log_line(item, action, result + " (승인: " + approver + ")"))
    change_status(item, "조치됨")
    return "실행 완료"


def reject_unauthorized(item, approver, action_log):
    action_log.append(log_line(item, "전체", "권한 없음 — 승인 시도: " + approver))
    return "권한 없음"


def apply_decision(item, decision, state, action_log):
    approver = decision["approver"]
    if not is_authorized(approver):
        return reject_unauthorized(item, approver, action_log)
    return finish_decision(item, decision, state, action_log)


def finish_decision(item, decision, state, action_log):
    approver = decision["approver"]
    if decision["result"] == "승인":
        return execute_actions(item, state, action_log, approver)
    change_status(item, "종료")
    action_log.append(
        log_line(
            item,
            "전체",
            "거절됨 (승인: " + approver + " — " + decision["comment"] + ")",
        )
    )
    return "거절 처리"
