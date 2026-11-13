import sys

from incident import load_json
from report import (
    count_by_rule,
    find_late_tickets,
    find_missing_incidents,
    make_report_lines,
    make_ticket_table,
    mean_ack_by_grade,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPORT_PATH = "incident_report_20261112.md"

tickets = load_json("day05_tickets.json")
actions = load_json("day05_actions.json")
print("--- 단계 1: 불러온 티켓", len(tickets), "장 · 조치 기록", len(actions), "건")

table = make_ticket_table(tickets)
rule_counts = count_by_rule(table)
grade_means = mean_ack_by_grade(table)
late_tickets = find_late_tickets(table)
missing = find_missing_incidents(actions, tickets)

print("--- 단계 2: 규칙별 티켓 수")
for rule in rule_counts:
    print(rule, ":", rule_counts[rule], "장")

print("--- 단계 3: 등급별 평균 확인 시간(분)")
for grade in grade_means:
    print(grade, ":", grade_means[grade], "분")

print("--- 단계 4: 응답 기한을 넘겨 확인한 티켓", len(late_tickets), "장 · 티켓이 없는 조치", len(missing), "건")
for ticket in late_tickets:
    print(ticket["id"], "기한", ticket["sla_due"], "분 · 확인", ticket["acked_at"], "분")
for action in missing:
    print(action["incident"], action["action"], action["target"], "→ 티켓 없음")

lines = make_report_lines(tickets, actions, rule_counts, grade_means, late_tickets, missing)
text = "\n".join(lines) + "\n"
with open(REPORT_PATH, "w", encoding="utf-8") as report_file:
    report_file.write(text)
print("--- 단계 5: 리포트 파일", REPORT_PATH, "·", len(lines), "줄 저장")
