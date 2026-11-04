import pandas as pd

EVENTS_PATH = "normalized_events.json"
TRAFFIC_PATH = "baseline_traffic.csv"
SPIKE_MULTIPLE = 3


def load_events(path):
    """Load normalized events into a pandas table."""
    events = pd.read_json(path)
    return events


def add_minute_column(events):
    """Add a minute-rounded timestamp column to each event."""
    times = pd.to_datetime(events["time"])
    minutes = times.dt.floor("min")
    events["minute"] = minutes
    return events


def count_web_per_minute(events):
    """Count web events grouped by minute."""
    is_web = events["source"] == "web"
    web_events = events[is_web]
    counts = web_events.groupby("minute").size()
    return counts


def make_traffic_limit(path, multiple):
    """Return the baseline requests-per-minute average times a multiplier."""
    baseline = pd.read_csv(path)
    average = baseline["requests_per_minute"].mean()
    limit = average * multiple
    return limit


def pick_spike_minutes(counts, limit):
    """Keep minutes whose request count meets or exceeds the limit."""
    is_spike = counts >= limit
    spike_minutes = counts[is_spike]
    return spike_minutes
