import pandas as pd

ALERTS_PATH = "tuning_alerts.json"  # Day 3 출력(alerts.json)과 겹치지 않게 분리
IP_RULE = "SaaS 평소와 다른 IP"
TRUSTED_IPS = ["203.0.113.80"]


def load_table(path):
    return pd.read_json(path)


def count_false_alarms(alerts):
    is_real = alerts["real"]
    is_false = ~is_real
    false_alarms = alerts[is_false]
    false_alarm_count = len(false_alarms)
    return false_alarm_count


def apply_exception(alerts):
    is_ip_rule = alerts["rule"] == IP_RULE
    is_trusted = alerts["ip"].isin(TRUSTED_IPS)
    is_removed = is_ip_rule & is_trusted
    removed_alerts = alerts[is_removed]
    is_kept = ~is_removed
    kept_alerts = alerts[is_kept]
    return removed_alerts, kept_alerts


def count_real_removed(removed_alerts):
    is_real_removed = removed_alerts["real"]
    real_removed = removed_alerts[is_real_removed]
    real_removed_count = len(real_removed)
    return real_removed_count


def find_removed_users(removed_alerts):
    removed_users = removed_alerts["user"].unique()
    return removed_users
