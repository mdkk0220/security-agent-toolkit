from tuning import (
    ALERTS_PATH,
    apply_exception,
    count_false_alarms,
    count_real_removed,
    find_removed_users,
    load_table,
)

alerts = load_table(ALERTS_PATH)
alert_count = len(alerts)
false_alarm_count_before = count_false_alarms(alerts)
print("--- 단계 1: 예외 규칙을 적용하기 전 ---")
print("알림 수:", alert_count)
print("오탐 수:", false_alarm_count_before)

removed_alerts, kept_alerts = apply_exception(alerts)
removed_count = len(removed_alerts)
print("--- 단계 2: 예외 규칙으로 빠진 알림 ---")
print("빠진 알림 수:", removed_count)
for alert in removed_alerts.to_dict("records"):
    print("빠진 알림:", alert["id"], alert["rule"], alert["user"], alert["ip"])
removed_users = find_removed_users(removed_alerts)
print("빠진 알림의 사용자:", removed_users)

kept_count = len(kept_alerts)
false_alarm_count_after = count_false_alarms(kept_alerts)
print("--- 단계 3: 예외 규칙을 적용한 뒤 ---")
print("알림 수:", kept_count)
print("오탐 수:", false_alarm_count_after)

real_removed_count = count_real_removed(removed_alerts)
print("--- 단계 4: 빠진 알림 중 진짜 문제였던 것 ---")
print("진짜 문제였던 알림 수:", real_removed_count)
