from account_actions import lock_account
from session_actions import terminate_sessions


def contain_account(user, state, vip_accounts, incident_id, reason):
    records = []
    lock_record = lock_account(user, state, vip_accounts, incident_id, reason)
    records.append(lock_record)
    if lock_record["after"] == "잠김":
        records.append(terminate_sessions(user, state, incident_id, reason))
    return records
