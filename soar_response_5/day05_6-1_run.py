import sys

from incident import load_json
from false_positive import handle_false_positive
from day4_check import check_report, check_gate, check_recovery, mark

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPORT_PATH = "incident_report_20261112.md"
TRUE_POSITIVE_USERS = ["dami"]
NOW = 45

tickets = load_json("day05_tickets.json")
actions = load_json("day05_actions.json")
policy = load_json("config/approval_policy.json")
cases = load_json("gate_cases.json")
print("--- 단계 1: 점검 재료 · 티켓", len(tickets), "장 · 조치 기록", len(actions), "건 · 시험 사례", len(cases), "개")

with open(REPORT_PATH, encoding="utf-8") as report_file:
    report_text = report_file.read()
report_problems = check_report(report_text, tickets, actions)
gate_problems = check_gate(cases, policy)

state = load_json("fp_state.json")
log = load_json("fp_log.json")
results = []
for report in load_json("fp_reports.json"):
    result = handle_false_positive(report, log, state, NOW)
    results.append(result)
recovery_problems = check_recovery(results, state, TRUE_POSITIVE_USERS)

checks = [
    {"title": "① 2 · 3일 차 데이터가 리포트에 빠짐없이 들어갔다", "problems": report_problems},
    {"title": "② 위험 점수에 따라 자동 · 승인 필요 · 차단 금지가 맞게 나뉜다", "problems": gate_problems},
    {"title": "③ 오탐 복구가 30분 안에 빠짐없이 끝났고 진짜 공격의 잠금은 그대로다", "problems": recovery_problems},
]
print("--- 단계 2: Day 4 점검 목록")
lines = ["# Day 4 마무리 점검 — 2026-11-13(금)", ""]
for check in checks:
    result_mark = mark(check["problems"])
    print("[" + result_mark + "]", check["title"], "· 문제", len(check["problems"]), "개")
    lines.append("- [" + result_mark + "] " + check["title"])
    for problem in check["problems"]:
        print("   -", problem)
        lines.append("  - " + problem)

text = "\n".join(lines) + "\n"
with open("day4_checklist.md", "w", encoding="utf-8") as check_file:
    check_file.write(text)
print("--- 단계 3: day4_checklist.md", len(lines), "줄 저장")
