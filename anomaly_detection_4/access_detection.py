import pandas as pd

from rbac import check_permission

EVENTS_PATH = "normalized_events.json"
REPEAT_LIMIT = 3
PRIORITY = {"퇴사한 계정": 1, "권한 없음": 2, "허용": 3}


def load_events(path):
    """Load normalized events into a DataFrame."""
    return pd.read_json(path)


def pick_server_failures(events):
    """Select failed events from the authorization server."""
    is_server = events["source"] == "server"
    is_fail = events["result"] == "실패"
    return events[is_server & is_fail]


def pick_suspicious(server_failures):
    """Select failures belonging to users with repeated failures."""
    users = server_failures["user"]
    user_counts = users.value_counts()
    repeated_users = user_counts[user_counts >= REPEAT_LIMIT]
    repeated_names = repeated_users.index
    is_repeated_user = users.isin(repeated_names)
    suspicious = server_failures[is_repeated_user]
    return suspicious


def judge_failure(user, action):
    """Recheck a denied request against the RBAC rules and assign priority."""
    parts = action.split(":")
    resource = parts[0]
    permission_action = parts[1]
    is_allowed, reason = check_permission(user, resource, permission_action)
    priority = PRIORITY.get(reason, 4)
    return reason, priority
