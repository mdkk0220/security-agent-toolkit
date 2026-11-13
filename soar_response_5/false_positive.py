from rollback import find_incident_records, rollback_incident

RECOVERY_LIMIT = 30


def list_changes(log, incident_id):
    changes = []
    for record in find_incident_records(log, incident_id):
        if record["before"] != record["after"]:
            changes.append(record)
    return changes


def find_not_recovered(changes, state):
    remaining = []
    for record in changes:
        target = record["target"]
        if record["action"] == "계정 잠금" and target in state["locked_users"]:
            remaining.append(target)
        if record["action"] == "IP 차단" and target in state["blocked_ips"]:
            remaining.append(target)
    return remaining


def make_tuning_note(changes):
    for record in changes:
        if record["action"] == "IP 차단":
            return "허용 목록에 추가 검토: " + record["target"]
    first = changes[0]
    return "탐지 규칙 예외 검토: " + first["target"] + " (" + first["reason"] + ")"


def handle_false_positive(report, log, state, now):
    incident_id = report["incident"]
    changes = list_changes(log, incident_id)
    undo_records = rollback_incident(incident_id, log, state)
    remaining = find_not_recovered(changes, state)
    changed = []
    for record in changes:
        changed.append(record["action"] + " " + record["target"])
    undone = []
    for record in undo_records:
        undone.append(record["action"] + " " + record["target"])
    minutes = now - report["reported_at"]
    result = {
        "incident": incident_id,
        "changed": changed,
        "undone": undone,
        "remaining": remaining,
        "minutes": minutes,
        "in_time": minutes <= RECOVERY_LIMIT,
        "tuning": make_tuning_note(changes),
    }
    return result
