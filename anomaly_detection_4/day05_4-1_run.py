from final_check import (
    ALERTS_PATH,
    LOGIN_ALERTS_PATH,
    PROBLEMS_PATH,
    apply_exception,
    evaluate,
    load_table,
    make_summary,
    merge_alerts,
)

alerts = load_table(ALERTS_PATH)
login_alerts = load_table(LOGIN_ALERTS_PATH)
problems = load_table(PROBLEMS_PATH)

removed_alerts, kept_alerts = apply_exception(alerts)
removed_count = len(removed_alerts)
kept_count = len(kept_alerts)
print("--- 단계 1: 믿는 IP 예외 규칙 적용 ---")
print("빠진 알림 수:", removed_count)
print("남은 알림 수:", kept_count)

all_alerts = merge_alerts(kept_alerts, login_alerts)
all_count = len(all_alerts)
print("--- 단계 2: 로그인 규칙의 알림 합치기 ---")
print("합친 뒤 알림 수:", all_count)

false_alarm_count, missed_problems = evaluate(all_alerts, problems)
print("--- 단계 3: 합친 알림의 오탐 ---")
print("오탐 수:", false_alarm_count)

missed_count = len(missed_problems)
print("--- 단계 4: 아직 놓친 진짜 문제 ---")
print("미탐 수:", missed_count)
for problem in missed_problems.to_dict("records"):
    print("놓친 문제:", problem["id"], problem["who"], problem["what"])

summary = make_summary(all_count, false_alarm_count, missed_count)
print("--- 단계 5: 한 문장 요약 ---")
print(summary)
