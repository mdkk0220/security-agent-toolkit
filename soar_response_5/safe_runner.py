from incident import change_status, make_log_entry, match_playbooks, run_action

DONE_STATUSES = ["조치됨", "보고됨", "종료"]
MAX_LOCKS_PER_RUN = 3


def find_skip_reason(action, entity, state):
    if action == "계정 잠금" and entity in state["locked_users"]:
        return "건너뜀: 이미 잠겨 있음"
    if action == "계정 잠금" and len(state["locked_users"]) >= MAX_LOCKS_PER_RUN:
        return "건너뜀: 한 번에 잠글 수 있는 계정 수를 넘음 (담당자 확인 필요)"
    return ""


def safe_run_action(action, incident, state):
    entity = incident["entity"]
    skip_reason = find_skip_reason(action, entity, state)
    if skip_reason != "":
        return skip_reason
    return run_action(action, incident, state)


def run_playbook_safe(incident, playbook, state, action_log):
    if incident["status"] in DONE_STATUSES:
        entry = make_log_entry(incident, playbook, "전체", "이미 처리됨 — 건너뜀")
        action_log.append(entry)
        return "이미 처리됨"
    change_status(incident, "분류됨")
    if playbook["approval"] != "자동":
        entry = make_log_entry(incident, playbook, "전체", "승인 대기")
        action_log.append(entry)
        return "승인 대기"
    skipped = False
    for action in playbook["actions"]:
        result = safe_run_action(action, incident, state)
        if result.startswith("건너뜀"):
            skipped = True
        entry = make_log_entry(incident, playbook, action, result)
        action_log.append(entry)
    if skipped:
        return "일부 건너뜀"
    change_status(incident, "조치됨")
    return "실행 완료"


def process_safe(incidents, registry, state, action_log):
    counts = {}
    for incident in incidents:
        playbooks = match_playbooks(incident, registry)
        if not playbooks:
            result_text = "맞는 플레이북 없음"
        else:
            result_text = "맞는 플레이북 없음"
            for playbook in playbooks:
                result_text = run_playbook_safe(incident, playbook, state, action_log)
        counts[result_text] = counts.get(result_text, 0) + 1
        print(
            incident["id"],
            incident["entity"],
            "->",
            result_text,
            "(상태: " + incident["status"] + ")",
        )
    return counts
