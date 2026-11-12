from notifier import notify

MAX_TRIES = 3


def pick_recipients(grade, rules):
    table = rules["recipients"]
    return table[grade]


def should_send(ticket, now, gap):
    if ticket["notified_count"] == 0:
        return True
    elapsed = now - ticket["last_notified"]
    return elapsed >= gap


def send_with_retry(message, url, max_tries):
    for attempt in range(1, max_tries + 1):
        if notify(message, url):
            return attempt
    return 0


def send_ticket_notice(ticket, now, rules):
    if not should_send(ticket, now, rules["send_gap_minutes"]):
        return "건너뜀"
    recipients = pick_recipients(ticket["grade"], rules)
    names = ""
    for name in recipients:
        if names != "":
            names = names + ", "
        names = names + name
    message = (
        ticket["title"]
        + " · "
        + ticket["id"]
        + " · 알림 "
        + str(ticket["count"])
        + "건 · 기한 "
        + str(ticket["sla_due"])
        + "분 · 수신: "
        + names
    )
    attempt = send_with_retry(message, rules["alert_url"], MAX_TRIES)
    if attempt == 0:
        return "실패"
    ticket["notified_count"] = ticket["notified_count"] + 1
    ticket["last_notified"] = now
    return "전송"
