DEFAULT_NEXT_STEP = "담당자가 알림 내용을 읽고 필요한 일을 정한다"
MANUAL_STEP = "조치가 확인되지 않았다. 담당자가 직접 계정이나 IP 상태를 보고 조치한다"
NEXT_STEPS = {
    "조치됨": "조치 결과가 맞는지 확인하고 계정이나 IP 상태를 점검한다",
    "승인 대기": "승인할지 거절할지 정하고 정한 사람의 이름을 남긴다",
    "조치 없음": "자동 조치가 없는 알림이니 직접 보고 조치가 필요한지 정한다",
}


def make_title(alert):
    grade = alert["grade"]
    entity = alert["entity"]
    rule = alert["rule"]
    return "[" + grade + "] " + entity + " — " + rule


def find_next_step(alert, next_steps):
    status = alert["status"]
    return next_steps.get(status, DEFAULT_NEXT_STEP)


def has_failed_action(done_list):
    for text in done_list:
        if "확인 실패" in text:
            return True
    return False


def make_ticket(alert, ticket_no, rules, next_steps):
    sla_table = rules["sla_minutes"]
    sla_minutes = sla_table[alert["grade"]]
    sla_due = alert["minute"] + sla_minutes
    needs_manual = has_failed_action(alert["done"])
    next_step = find_next_step(alert, next_steps)
    if needs_manual:
        next_step = MANUAL_STEP
    ticket = {
        "id": "TCK-" + str(ticket_no),
        "title": make_title(alert),
        "entity": alert["entity"],
        "rule": alert["rule"],
        "grade": alert["grade"],
        "playbook": alert["playbook"],
        "done": alert["done"],
        "status": "열림",
        "next_step": next_step,
        "needs_manual": needs_manual,
        "created_at": alert["minute"],
        "updated_at": alert["minute"],
        "sla_due": sla_due,
        "count": 1,
        "incidents": [alert["id"]],
        "notified_count": 0,
        "last_notified": -1,
        "acked_at": -1,
        "resolved_at": -1,
        "escalation_level": 0,
        "comments": [],
    }
    return ticket
