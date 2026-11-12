from incident import load_json, save_json
from ticket_merge import handle_alert
from ticket_notice import send_ticket_notice, send_with_retry, MAX_TRIES

alerts = load_json("alerts_thu.json")
rules = load_json("config/escalation_rules.json")
tickets = []
sent_count = 0
skipped_count = 0

print("--- 단계 1: 알림", len(alerts), "건 처리와 담당자 알리기")
for alert in alerts:
    ticket, action = handle_alert(alert, tickets, rules)
    result = send_ticket_notice(ticket, alert["minute"], rules)
    print(alert["id"], "->", ticket["id"], action, "· 담당자 알리기:", result)
    if result == "전송":
        sent_count = sent_count + 1
    if result == "건너뜀":
        skipped_count = skipped_count + 1

print("--- 단계 2: 담당자에게 전송", sent_count, "건 · 건너뜀", skipped_count, "건")
for ticket in tickets:
    print(
        ticket["id"],
        "담당자에게 알린 횟수",
        ticket["notified_count"],
        "번 · 마지막으로 알린 시각",
        ticket["last_notified"],
        "분",
    )

url_off = "http://127.0.0.1:5999/alert"
print("--- 단계 3: 꺼진 주소로 최대", MAX_TRIES, "번 보내 보기")
attempt = send_with_retry("[테스트] 꺼진 알림 서버", url_off, MAX_TRIES)
print("성공한 시도 번호:", attempt, "(0 은 모두 실패)")

save_json(tickets, "tickets_day4.json")
saved = load_json("tickets_day4.json")
print("--- 단계 4: 파일에 저장된 티켓", len(saved), "장")
