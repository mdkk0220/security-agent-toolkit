import pandas as pd

ALERTS_PATH = "tuning_alerts.json"  # Day 3 출력(alerts.json)과 겹치지 않게 분리
PROBLEMS_PATH = "problems.json"


def load_table(path):
    return pd.read_json(path)


def pick_real_alerts(alerts):
    is_real = alerts["real"]
    real_alerts = alerts[is_real]
    return real_alerts


def find_false_alarms(alerts):
    is_real = alerts["real"]
    is_false = ~is_real
    false_alarms = alerts[is_false]
    false_alarm_rule_counts = false_alarms["rule"].value_counts()
    return false_alarms, false_alarm_rule_counts


def find_missed(problems, real_alerts):
    caught_ids = real_alerts["problem"]
    is_caught = problems["id"].isin(caught_ids)
    is_missed = ~is_caught
    missed_problems = problems[is_missed]
    return missed_problems


def count_real_alerts(alerts):
    is_real = alerts["real"]
    real_alert_count = is_real.sum()
    return real_alert_count
