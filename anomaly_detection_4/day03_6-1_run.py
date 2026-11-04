import json

from alerts import ALERTS_PATH, make_login_alerts, make_traffic_alerts, save_alerts
from login_detection import (
    EVENTS_PATH,
    LOGIN_LIMIT,
    count_by_ip,
    load_events,
    pick_alert_ips,
    pick_login_failures,
)
from traffic_detection import (
    SPIKE_MULTIPLE,
    TRAFFIC_PATH,
    add_minute_column,
    count_web_per_minute,
    make_traffic_limit,
    pick_spike_minutes,
)

events = load_events(EVENTS_PATH)
login_failures = pick_login_failures(events)
login_counts = count_by_ip(login_failures)
alert_ips = pick_alert_ips(login_counts, LOGIN_LIMIT)
login_alerts = make_login_alerts(alert_ips)
login_alert_count = len(login_alerts)
print("--- 단계 1: 로그인 실패 알림", login_alert_count, "건")

events = add_minute_column(events)
minute_counts = count_web_per_minute(events)
limit = make_traffic_limit(TRAFFIC_PATH, SPIKE_MULTIPLE)
spike_minutes = pick_spike_minutes(minute_counts, limit)
traffic_alerts = make_traffic_alerts(spike_minutes)
traffic_alert_count = len(traffic_alerts)
print("--- 단계 2: 트래픽 급증 알림", traffic_alert_count, "건")

all_alerts = login_alerts + traffic_alerts
saved_count = save_alerts(all_alerts, ALERTS_PATH)
print("--- 단계 3:", ALERTS_PATH, "에 알림", saved_count, "건 저장")

with open(ALERTS_PATH, encoding="utf-8") as file:
    saved_alerts = json.load(file)
print("--- 단계 4: 저장된 알림")
for alert in saved_alerts:
    print(alert)
