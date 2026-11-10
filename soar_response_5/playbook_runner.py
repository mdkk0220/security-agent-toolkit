from incident import change_status, make_log_entry, match_playbooks, run_action


def run_playbook(incident, playbook, state, action_log):
    change_status(incident, "분류됨")
    if playbook["approval"] != "자동":
        action_log.append(make_log_entry(incident, playbook, "전체", "승인 대기"))
        return False
    for action in playbook["actions"]:
        result = run_action(action, incident, state)
        action_log.append(make_log_entry(incident, playbook, action, result))
    change_status(incident, "조치됨")
    return True


def process_incidents(incidents, registry, state, action_log):
    pending = []
    for incident in incidents:
        playbooks = match_playbooks(incident, registry)
        result_text = "맞는 플레이북 없음"
        for playbook in playbooks:
            done = run_playbook(incident, playbook, state, action_log)
            if done:
                result_text = playbook["id"] + " 실행 완료"
            else:
                result_text = playbook["id"] + " 승인 대기"
                waiting = {
                    "incident": incident["id"],
                    "entity": incident["entity"],
                    "playbook": playbook["id"],
                    "approval": playbook["approval"],
                }
                pending.append(waiting)
        status_text = "(상태: " + incident["status"] + ")"
        print(
            incident["id"],
            incident["entity"],
            incident["grade"],
            "->",
            result_text,
            status_text,
        )
    return pending
