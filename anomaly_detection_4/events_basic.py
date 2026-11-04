import pandas as pd

EVENTS_PATH = "normalized_events.json"


def load_events(path):
    """Read normalized JSON events into a pandas table."""
    events = pd.read_json(path)
    return events


def describe_events(events):
    """Return the table shape and its first three timestamps."""
    shape = events.shape
    times = events["time"]
    first_times = times.head(3)
    return shape, first_times


def pick_failed(events):
    """Return only events marked as failures."""
    results = events["result"]
    is_fail = results == "실패"
    failed = events[is_fail]
    return failed


def count_values(table, column):
    """Count each value in the named column."""
    values = table[column]
    counts = values.value_counts()
    return counts
