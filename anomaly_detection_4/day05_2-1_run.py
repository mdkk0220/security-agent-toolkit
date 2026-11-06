from evaluation import (
    ALERTS_PATH,
    PROBLEMS_PATH,
    count_real_alerts,
    find_false_alarms,
    find_missed,
    load_table,
    pick_real_alerts,
)

alerts = load_table(ALERTS_PATH)
problems = load_table(PROBLEMS_PATH)
alert_count = len(alerts)
print("--- 단계 1: 알림 전체 ---")
print("알림 수:", alert_count)

real_alerts = pick_real_alerts(alerts)
real_alert_count = count_real_alerts(alerts)
print("--- 단계 2: 진짜 문제였던 알림 (맞게 찾은 알림) ---")
print("진짜 문제였던 알림 수:", real_alert_count)

false_alarms, false_alarm_rule_counts = find_false_alarms(alerts)
false_alarm_count = len(false_alarms)
print("--- 단계 3: 오탐 (문제가 아닌데 난 알림) ---")
print("오탐 수:", false_alarm_count)
print("오탐이 난 규칙과 오탐 수:")
print(false_alarm_rule_counts)

missed_problems = find_missed(problems, real_alerts)
missed_count = len(missed_problems)
print("--- 단계 4: 미탐 (알림이 나지 않은 진짜 문제) ---")
print("미탐 수:", missed_count)
for problem in missed_problems.to_dict("records"):
    print("놓친 문제:", problem["id"], problem["who"], problem["what"])
