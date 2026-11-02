import json
from datetime import datetime

from checklist import TIME_FORMAT, load_state, run_checklist
from log_summary import read_log
from weekly_report import build_report, save_report

TODAY = "2026-11-02"
NOW = datetime.strptime(TODAY + " 10:00", TIME_FORMAT)
with open("config/alert.json", encoding="utf-8") as alert_file:
    ALERT = json.load(alert_file)

print("--- 단계 1: 모으기 - 점검 결과와 요청 로그")
state = load_state("config/week_state.json")
results = run_checklist(state, NOW)
entries = read_log("week_log.jsonl")
print("점검", len(results), "가지 · 요청", len(entries), "건")
print("--- 단계 2: 보고서 만들기와 저장")
text = build_report(results, entries, ALERT, TODAY)
file_name = save_report(text, TODAY)
print("저장한 파일:", file_name)
print("--- 단계 3: 저장한 보고서 내용")
print(text)
