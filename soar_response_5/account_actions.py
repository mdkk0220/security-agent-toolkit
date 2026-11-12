from containment_store import make_record


def check_policy(user, vip_accounts):
    if user in vip_accounts:
        return "VIP 계정이라 자동 조치 대상이 아님"
    return ""


def verify_locked(user, state):
    return user in state["locked_users"]


def lock_account(user, state, vip_accounts, incident_id, reason):
    blocked = check_policy(user, vip_accounts)
    if blocked != "":
        return make_record("계정 잠금", user, incident_id, "변경 없음", "변경 없음", blocked)
    if user in state["locked_users"]:
        return make_record(
            "계정 잠금", user, incident_id, "잠김", "잠김", "이미 잠겨 있어 변경 없음"
        )
    state["locked_users"].append(user)
    after = "잠김"
    if not verify_locked(user, state):
        after = "잠기지 않음 (확인 실패)"
    return make_record("계정 잠금", user, incident_id, "잠기지 않음", after, reason)


def unlock_account(user, state, incident_id, reason):
    if user not in state["locked_users"]:
        return make_record(
            "계정 해제",
            user,
            incident_id,
            "잠기지 않음",
            "잠기지 않음",
            "잠겨 있지 않아 변경 없음",
        )
    state["locked_users"].remove(user)
    after = "잠기지 않음"
    if verify_locked(user, state):
        after = "잠김 (확인 실패)"
    return make_record("계정 해제", user, incident_id, "잠김", after, reason)
