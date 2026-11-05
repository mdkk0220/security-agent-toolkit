from access_detection import EVENTS_PATH, load_events
from correlation import find_chains_in_events
from risk_scores import (
    RISK_PATH,
    collect_findings,
    collect_reasons,
    make_records,
    save_records,
    score_findings,
)

events = load_events(EVENTS_PATH)
chains = find_chains_in_events(events)
findings = collect_findings(events, chains)
print("--- 단계 1: 탐지된 규칙", len(findings), "건")

totals = score_findings(findings)
print("--- 단계 2: 대상별 점수")
print(totals)

reasons = collect_reasons(findings)
records = make_records(totals, reasons)
saved_count = save_records(records, RISK_PATH)
print("--- 단계 3:", RISK_PATH, "에", saved_count, "건 저장")

print("--- 단계 4: 등급 · 대상 · 점수 · 이유")
for record in records:
    print(record["grade"], record["entity"], record["score"], record["reasons"])
