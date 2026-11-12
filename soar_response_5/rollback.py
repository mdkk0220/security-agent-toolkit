from containment_store import make_record
from undo_actions import undo_record

UNDOABLE_ACTIONS = ["계정 잠금", "IP 차단"]


def find_incident_records(log, incident_id):
    found = []
    for record in log:
        action_name = record["action"]
        if record["incident"] == incident_id:
            found.append(record)
    return list(reversed(found))


def should_undo(record):
    if record["before"] == record["after"]:
        return False
    if "확인 실패" in record["after"]:
        return False
    return record["action"] in UNDOABLE_ACTIONS


def rollback_incident(incident_id, log, state):
    records = []
    for record in find_incident_records(log, incident_id):
        if should_undo(record):
            records.append(undo_record(record, state))
        if record["before"] != record["after"] and not should_undo(record):
            note = (
                "되돌릴 수 없는 조치("
                + record["action"]
                + ") — 사용자가 다시 로그인해야 함"
            )
            records.append(
                make_record(
                    "되돌리기 불가",
                    record["target"],
                    incident_id,
                    record["before"],
                    record["after"],
                    note,
                )
            )
    return records
