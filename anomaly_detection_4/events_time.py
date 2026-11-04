import pandas as pd

EVENTS_PATH = "normalized_events.json"
FAILED_PATH = "failed_events.csv"


def load_events(path):
    """Read normalized JSON events into a pandas table."""
    events = pd.read_json(path)
    return events


def pick_failed(events):
    """Return only events marked as failures."""
    results = events["result"]
    is_fail = results == "실패"
    failed = events[is_fail]
    return failed


def count_by_user(failed):
    """Count failed events by user, excluding missing user values."""
    grouped = failed.groupby("user")
    counts = grouped.size()
    sorted_counts = counts.sort_values(ascending=False)
    return sorted_counts


def add_hour(events):
    """Add an hour column derived from the event timestamp."""
    times = pd.to_datetime(events["time"])
    hours = times.dt.hour
    events["hour"] = hours
    return events


def count_by_hour(failed):
    """Count failed events by hour."""
    grouped = failed.groupby("hour")
    counts = grouped.size()
    return counts


def save_failed(failed, path):
    """Save failed events to CSV without the dataframe index."""
    failed.to_csv(path, index=False)
