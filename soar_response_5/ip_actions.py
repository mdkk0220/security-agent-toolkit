from containment_store import make_record

SHARED_IP_LIMIT = 2
DEFAULT_TTL = 120


def is_in_allowlist(ip, allowlist_ips):
    return ip in allowlist_ips


def count_users_on_ip(ip, ip_users):
    return len(ip_users.get(ip, []))


def check_ip_policy(ip, allowlist_ips, ip_users):
    if is_in_allowlist(ip, allowlist_ips):
        return "허용 목록 IP 라서 차단하지 않음"
    if count_users_on_ip(ip, ip_users) >= SHARED_IP_LIMIT:
        return "여러 계정이 함께 쓰는 IP 라서 담당자 승인 필요"
    return ""


def block_ip(ip, state, incident_id, reason, ttl):
    state["blocked_ips"].append(ip)
    state["block_expiry"][ip] = state["clock"] + ttl
    after = "차단됨"
    if ip not in state["blocked_ips"]:
        after = "차단되지 않음 (확인 실패)"
    return make_record(
        "IP 차단",
        ip,
        incident_id,
        "차단되지 않음",
        after,
        reason + " (" + str(ttl) + "분 뒤 자동 해제)",
    )


def unblock_ip(ip, state, incident_id, reason):
    state["blocked_ips"].remove(ip)
    state["block_expiry"].pop(ip)
    return make_record("IP 해제", ip, incident_id, "차단됨", "차단되지 않음", reason)


def expire_blocks(state, incident_id):
    records = []
    for ip in list(state["blocked_ips"]):
        end_time = state["block_expiry"][ip]
        if end_time <= state["clock"]:
            records.append(
                unblock_ip(ip, state, incident_id, "차단 시간이 끝나 자동 해제")
            )
    return records
