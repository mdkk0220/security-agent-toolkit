from exception_policy import EXCEPTIONS
from rbac import check_permission


def grant_request(request):
    """Recheck policy and grant a temporary exception for an approved request."""
    if request["status"] != "approved":
        return False, "승인되지 않음"
    ok, judge_reason = check_permission(request["user"], request["resource"], request["action"])
    if ok or judge_reason != "권한 없음":
        return False, f"부여하지 않음({judge_reason})"
    exception = {
        "id": len(EXCEPTIONS) + 1,
        "user": request["user"],
        "permission": request["permission"],
        "expires": request["until"],
        "reason": request["reason"],
    }
    EXCEPTIONS.append(exception)
    request["exception_id"] = exception["id"]
    request["status"] = "granted"
    return True, "부여"
