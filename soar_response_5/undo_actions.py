from account_actions import unlock_account
from ip_actions import unblock_ip


def undo_account(record, state):
    return unlock_account(
        record["target"],
        state,
        record["incident"],
        "되돌리기: " + record["reason"],
    )


def undo_ip(record, state):
    return unblock_ip(
        record["target"],
        state,
        record["incident"],
        "되돌리기: " + record["reason"],
    )


def undo_record(record, state):
    if record["action"] == "계정 잠금":
        return undo_account(record, state)
    return undo_ip(record, state)
