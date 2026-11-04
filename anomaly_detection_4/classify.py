import pandas as pd

EVENTS_PATH = "normalized_events.json"
TYPE_ORDER = ["비정상 로그인", "비인가 접근", "기타 실패", "정상"]


def load_events(path):
    """Load normalized events into a pandas table."""
    events = pd.read_json(path)
    return events


def classify_event(action, result):
    """Classify an event using ordered, first-match rules."""
    if result == "실패" and action == "POST /login":
        return "비정상 로그인"
    if result == "실패" and "/admin" in action:
        return "비인가 접근"
    if result == "실패":
        return "기타 실패"
    return "정상"


def count_types(events):
    """Count events by classification."""
    event_list = events.to_dict("records")
    counts = {}
    for event in event_list:
        action = event["action"]
        result = event["result"]
        type_name = classify_event(action, result)
        counts[type_name] = counts.get(type_name, 0) + 1
    return counts
