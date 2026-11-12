from incident import load_json
from ticket_merge import change_ticket_status
from escalation import overdue_minutes, needs_escalation, escalate_ticket

tickets = load_json("tickets_day4.json")
rules = load_json("config/escalation_rules.json")
steps_count = len(rules["escalation_steps"])
print("--- 단계 1: 불러온 티켓", len(tickets), "장 · 올림 단계", steps_count, "개")
escalated_count = 0

print("--- 단계 2: 점검 시각마다 상급자에게 올릴 티켓 찾기")
for now in [20, 60, 110]:
    print("[" + str(now) + "분] 점검")
    for ticket in tickets:
        if needs_escalation(ticket, now):
            result = escalate_ticket(ticket, now, rules)
            overdue = overdue_minutes(ticket, now)
            print(
                ticket["id"],
                ticket["title"],
                "→",
                result,
                "· 기한을",
                overdue,
                "분 넘김 · 올림 단계",
                ticket["escalation_level"],
            )
            if result == "올림":
                escalated_count = escalated_count + 1
    if now == 20:
        change_ticket_status(tickets[0], "확인 중", 25, "kim.sec")
        print("[25분] TCK-1 → 확인 중 · kim.sec")

print("--- 단계 3: 올린 결과 요약 (올린 횟수", escalated_count, "번)")
for ticket in tickets:
    if ticket["escalation_level"] > 0:
        print(
            ticket["id"],
            "올림 단계",
            ticket["escalation_level"],
            "· 상태",
            ticket["status"],
        )
