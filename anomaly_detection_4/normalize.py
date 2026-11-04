import json
from normalize_web import normalize_web
from normalize_json_csv import load_server, load_saas

EVENTS_PATH = "normalized_events.json"


def load_web(path):
    """Load and normalize valid web access-log lines."""
    events = []
    with open(path, encoding="utf-8") as web_file:
        for line in web_file:
            event = normalize_web(line)
            if event is not None:
                events.append(event)
    return events


def get_time(event):
    """Return an event timestamp for sorting."""
    return event["time"]


def merge_events(web, server, saas):
    """Combine the event lists and sort them chronologically."""
    events = web + server + saas
    events.sort(key=get_time)
    return events


def count_by_source(events):
    """Count events for each source."""
    counts = {}
    for event in events:
        source = event["source"]
        counts[source] = counts.get(source, 0) + 1
    return counts


def count_missing(events, key):
    """Count events whose specified field is None."""
    missing = 0
    for event in events:
        if event[key] is None:
            missing = missing + 1
    return missing


def save_events(events, path):
    """Save normalized events to a JSON file."""
    with open(path, "w", encoding="utf-8") as events_file:
        json.dump(events, events_file, ensure_ascii=False, indent=2)
