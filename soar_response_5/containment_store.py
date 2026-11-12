import copy

from incident import load_json, save_json

STATE_PATH = "containment_state.json"
LOG_PATH = "containment_log.json"
INITIAL_STATE = {
    "locked_users": ["junho"],
    "blocked_ips": [],
    "block_expiry": {},
    "clock": 0,
    "sessions": {
        "dami": ["S-101", "S-102"],
        "seoyeon": ["S-201"],
        "gaeun": ["S-301"],
        "jiwoo": ["S-401"],
        "junho": ["S-501"],
        "hana": ["S-601"],
    },
}


def new_state():
    """Return a fresh copy of the simulated system state."""
    return copy.deepcopy(INITIAL_STATE)


def save_state(state):
    save_json(state, STATE_PATH)


def load_state():
    return load_json(STATE_PATH)


def reset_log():
    save_json([], LOG_PATH)


def make_record(action, target, incident_id, before, after, reason):
    return {
        "action": action,
        "target": target,
        "incident": incident_id,
        "before": before,
        "after": after,
        "reason": reason,
    }


def append_log(record):
    try:
        log = load_json(LOG_PATH)
    except FileNotFoundError:
        log = []
    log.append(record)
    save_json(log, LOG_PATH)
