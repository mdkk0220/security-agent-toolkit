import pandas as pd

ALERTS_PATH = "tuning_alerts.json"  # Day 3 출력(alerts.json)과 겹치지 않게 분리
LOGIN_ALERTS_PATH = "login_alerts.json"
PROBLEMS_PATH = "problems.json"
IP_RULE = "SaaS 평소와 다른 IP"
TRUSTED_IPS = ["203.0.113.80"]


def load_table(path):
    return pd.read_json(path)


def apply_exception(alerts):
    is_ip_rule = alerts["rule"] == IP_RULE
    is_trusted = alerts["ip"].isin(TRUSTED_IPS)
    is_removed = is_ip_rule & is_trusted
    removed_alerts = alerts[is_removed]
    is_kept = ~is_removed
    kept_alerts = alerts[is_kept]
    return removed_alerts, kept_alerts


def merge_alerts(alerts, login_alerts):
    all_alerts = pd.concat([alerts, login_alerts])
    return all_alerts


def evaluate(all_alerts, problems):
    is_real = all_alerts["real"]
    is_false = ~is_real
    false_alarms = all_alerts[is_false]
    false_alarm_count = len(false_alarms)
    caught_ids = all_alerts["problem"].dropna()
    is_caught = problems["id"].isin(caught_ids)
    is_missed = ~is_caught
    missed_problems = problems[is_missed]
    return false_alarm_count, missed_problems


def make_summary(alert_count, false_alarm_count, missed_count):
    summary = (
        "알림 "
        + str(alert_count)
        + "개 중 오탐 "
        + str(false_alarm_count)
        + "개 · 놓친 문제 "
        + str(missed_count)
        + "개"
    )
    return summary
