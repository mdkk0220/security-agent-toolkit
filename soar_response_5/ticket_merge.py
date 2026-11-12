from ticketing import make_ticket, has_failed_action, NEXT_STEPS, MANUAL_STEP

ALLOWED_MOVES = {
    "열림": ["확인 중", "해결"],
    "확인 중": ["해결"],
    "해결": [],
}


def find_open_ticket(tickets, alert, window):
    for ticket in tickets:
        if ticket["entity"] == alert["entity"] and ticket["rule"] == alert["rule"]:
            if ticket["status"] != "해결":
                gap = alert["minute"] - ticket["updated_at"]
                if gap <= window:
                    return ticket
    return None


def merge_alert(ticket, alert):
    ticket["count"] = ticket["count"] + 1
    ticket["incidents"].append(alert["id"])
    ticket["updated_at"] = alert["minute"]
    ticket["done"] = ticket["done"] + alert["done"]
    if has_failed_action(alert["done"]):
        ticket["needs_manual"] = True
        ticket["next_step"] = MANUAL_STEP


def handle_alert(alert, tickets, rules):
    window = rules["merge_window_minutes"]
    existing = find_open_ticket(tickets, alert, window)
    if existing is None:
        ticket_no = len(tickets) + 1
        ticket = make_ticket(alert, ticket_no, rules, NEXT_STEPS)
        tickets.append(ticket)
        return ticket, "새 티켓"
    merge_alert(existing, alert)
    return existing, "병합"


def change_ticket_status(ticket, new_status, minute, who):
    old_status = ticket["status"]
    if new_status not in ALLOWED_MOVES[old_status]:
        return False
    ticket["status"] = new_status
    if ticket["acked_at"] == -1:
        ticket["acked_at"] = minute
    if new_status == "해결":
        ticket["resolved_at"] = minute
    ticket["updated_at"] = minute
    comment = who + " · " + str(minute) + "분 · " + old_status + " → " + new_status
    ticket["comments"].append(comment)
    return True
