from containment_store import make_record


def terminate_sessions(user, state, incident_id, reason):
    before_count = len(state["sessions"].get(user, []))
    state["sessions"][user] = []
    after_count = len(state["sessions"].get(user, []))
    return make_record(
        "세션 종료",
        user,
        incident_id,
        "세션 " + str(before_count) + "개",
        "세션 " + str(after_count) + "개",
        reason,
    )


def find_open_sessions(state):
    gaps = []
    for user in state["locked_users"]:
        open_count = len(state["sessions"].get(user, []))
        if open_count > 0:
            gaps.append(user)
    return gaps
