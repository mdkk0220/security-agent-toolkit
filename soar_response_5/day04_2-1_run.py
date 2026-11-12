from incident import load_json
from ticketing import make_ticket, NEXT_STEPS

alerts = load_json("alerts_thu.json")
rules = load_json("config/escalation_rules.json")
sla_count = len(rules["sla_minutes"])
print("--- 단계 1: 불러온 알림", len(alerts), "건 · 응답 기한을 정한 등급", sla_count, "개")

tickets = []
manual_count = 0
print("--- 단계 2: 알림마다 만든 티켓")
for alert in alerts:
    ticket_no = len(tickets) + 1
    ticket = make_ticket(alert, ticket_no, rules, NEXT_STEPS)
    tickets.append(ticket)
    print(ticket["id"], ticket["title"], "· 만든 시각", ticket["created_at"], "분 · 기한", ticket["sla_due"], "분")
    if ticket["needs_manual"]:
        manual_count = manual_count + 1

print("--- 단계 3: 티켓 본문 예 (TCK-1)")
first = tickets[0]
print("제목:", first["title"])
print("조치 내역:")
for text in first["done"]:
    print(" -", text)
print("다음 할 일:", first["next_step"])
print("응답 기한:", first["sla_due"], "분 (만든 시각", first["created_at"], "분)")

print("--- 단계 4: 직접 확인이 필요한 티켓", manual_count, "건")
for ticket in tickets:
    if ticket["needs_manual"]:
        print(ticket["id"], ticket["title"], "→", ticket["next_step"])
