from incident import load_json, save_json
from ticket_merge import handle_alert, change_ticket_status
from ticket_notice import send_ticket_notice
from escalation import needs_escalation, escalate_ticket
from shift_metrics import (
    average,
    collect_response_times,
    collect_resolve_times,
    count_sla_breaches,
)

alerts = load_json("alerts_thu.json")
events = load_json("status_events.json")
rules = load_json("config/escalation_rules.json")
tickets = []

print(
    "--- 단계 1: 가상 근무 0분부터 180분까지 (알림",
    len(alerts),
    "건 · 담당자 동작",
    len(events),
    "건)",
)
for now in range(0, 181):
    for alert in alerts:
        if alert["minute"] == now:
            ticket, action = handle_alert(alert, tickets, rules)
            result = send_ticket_notice(ticket, now, rules)
            print(
                "[" + str(now) + "분]",
                alert["id"],
                "→",
                ticket["id"],
                action,
                "· 알리기",
                result,
            )
    for event in events:
        if event["minute"] == now:
            for ticket in tickets:
                if ticket["id"] == event["ticket"]:
                    change_ticket_status(
                        ticket,
                        event["status"],
                        now,
                        event["who"],
                    )
                    print(
                        "[" + str(now) + "분]",
                        ticket["id"],
                        "→",
                        event["status"],
                        "·",
                        event["who"],
                    )
    if now % 10 == 0:
        for ticket in tickets:
            if needs_escalation(ticket, now):
                result = escalate_ticket(ticket, now, rules)
                if result != "그대로":
                    print(
                        "[" + str(now) + "분]",
                        ticket["id"],
                        "상급자에게",
                        result,
                        "· 올림 단계",
                        ticket["escalation_level"],
                    )

print("--- 단계 2: 근무 지표")
ack_times = collect_response_times(tickets)
mtta = average(ack_times)
resolve_times = collect_resolve_times(tickets)
mttr = average(resolve_times)
late_count = count_sla_breaches(tickets, 180)
print(
    "티켓",
    len(tickets),
    "장 · 확인한 티켓",
    len(ack_times),
    "장 · 해결한 티켓",
    len(resolve_times),
    "장",
)
print("평균 확인 시간(MTTA):", mtta, "분")
print("평균 해결 시간(MTTR):", mttr, "분")
print("응답 기한을 넘긴 티켓:", late_count, "장")

print("--- 단계 3: 다음 근무자에게 넘길 티켓 (해결되지 않은 티켓)")
for ticket in tickets:
    if ticket["status"] != "해결":
        print(
            ticket["id"],
            ticket["title"],
            "· 상태",
            ticket["status"],
            "·",
            ticket["next_step"],
        )

save_json(tickets, "shift_tickets.json")
saved = load_json("shift_tickets.json")
print("--- 단계 4: 파일에 저장된 티켓", len(saved), "장")
