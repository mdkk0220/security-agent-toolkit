from datetime import datetime

from checklist import TIME_FORMAT, load_state, run_checklist

NOW = datetime.strptime("2026-11-02 10:00", TIME_FORMAT)
state = load_state("config/week_state.json")
users = state["users"]
exceptions = state["exceptions"]

print("--- 단계 1: 점검 대상 - 사용자", len(users), "명 · 예외", len(exceptions), "개")
results = run_checklist(state, NOW)
print("--- 단계 2: 점검 결과")
for result in results:
    name = result["name"]
    problems = result["problems"]
    if len(problems) == 0:
        print(name, "통과")
    else:
        print(name, "실패", problems)
