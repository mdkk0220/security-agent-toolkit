import pandas as pd

EVENTS_PATH = "normalized_events.json"
LOGIN_LIMIT = 5


def load_events(path):
    """Load normalized events into a pandas table."""
    events = pd.read_json(path)
    return events


def pick_login_failures(events):
    """Select failed POST /login events."""
    actions = events["action"]
    is_login = actions == "POST /login"
    results = events["result"]
    is_fail = results == "실패"
    both_true = is_login & is_fail
    login_failures = events[both_true]
    return login_failures


def count_by_ip(login_failures):
    """Count failed login events by source IP."""
    counts = login_failures.groupby("ip").size()
    return counts


def pick_alert_ips(counts, limit):
    """Keep IPs whose failure count meets the threshold."""
    is_many = counts >= limit
    alert_ips = counts[is_many]
    return alert_ips
