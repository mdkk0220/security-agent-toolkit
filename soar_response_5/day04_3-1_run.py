from incident import load_json
from ticket_merge import handle_alert, change_ticket_status

alerts = load_json("alerts_thu.json")
rules = load_json("config/escalation_rules.json")
tickets = []

window = rules["merge_window_minutes"]
print("--- 단계 1: 알림", len(alerts), "건 처리 (합치는 시간", window, "분)")
for alert in alerts:
    ticket, action = handle_alert(alert, tickets, rules)
    print(alert["id"], "->", ticket["id"], action, "· 합쳐진 알림", ticket["count"], "건")

print("--- 단계 2: 알림", len(alerts), "건 → 티켓", len(tickets), "장")
for ticket in tickets:
    print(ticket["id"], ticket["title"], "· 알림", ticket["incidents"], "· 상태", ticket["status"])

print("--- 단계 3: TCK-1 상태 바꾸기")
first = tickets[0]
moves = [("확인 중", "kim.sec", 50), ("해결", "kim.sec", 65), ("열림", "lee.soc", 70)]
for new_status, who, minute in moves:
    changed = change_ticket_status(first, new_status, minute, who)
    if changed:
        print(first["id"], "→", new_status, "· 바꾼 사람", who)
    else:
        reason = first["status"] + "에서는 갈 수 없음"
        print(first["id"], "→", new_status, "· 거절됨 ·", reason)
print("댓글 기록:")
for comment in first["comments"]:
    print(" -", comment)
