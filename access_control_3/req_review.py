def approve_request(request, approver):
    """Approve an open request unless the approver is the requester."""
    if request["status"] != "reviewing":
        return False, "검토 중이 아님"
    if request["user"] == approver:
        return False, "본인 요청은 처리할 수 없음"
    request["status"] = "approved"
    request["approver"] = approver
    return True, "승인"


def reject_request(request, approver):
    """Reject an open request unless the approver is the requester."""
    if request["status"] != "reviewing":
        return False, "검토 중이 아님"
    if request["user"] == approver:
        return False, "본인 요청은 처리할 수 없음"
    request["status"] = "rejected"
    request["approver"] = approver
    return True, "반려"
