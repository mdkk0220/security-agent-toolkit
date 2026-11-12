from incident import load_json
from containment_store import (
    append_log,
    load_state,
    make_record,
    new_state,
    reset_log,
    save_state,
)
from ip_actions import check_ip_policy, block_ip, expire_blocks, DEFAULT_TTL

allowlist_ips = load_json("config/allowlist_ips.json")
ip_users = load_json("ip_users.json")
requests = [
    ("INC-005", "198.51.100.90", "경로 스캔"),
    ("INC-009", "192.0.2.10", "경로 스캔"),
    ("INC-008", "192.0.2.41", "경로 스캔"),
]
state = new_state()
reset_log()

print("--- 단계 1: 차단 요청 3건")
for incident_id, ip, reason in requests:
    refusal = check_ip_policy(ip, allowlist_ips, ip_users)
    record = make_record("IP 차단", ip, incident_id, "변경 없음", "변경 없음", refusal)
    if refusal == "":
        record = block_ip(ip, state, incident_id, reason, DEFAULT_TTL)
    append_log(record)
    print(
        record["incident"],
        record["target"],
        "·",
        record["before"],
        "→",
        record["after"],
        "·",
        record["reason"],
    )

print("--- 단계 2: 차단 뒤 차단한 IP 와 끝나는 시각")
print("차단한 IP:", state["blocked_ips"])
print("차단이 끝나는 시각(분):", state["block_expiry"])

print("--- 단계 3: 시계를 120분 뒤로 옮기고 시간이 끝난 차단 풀기")
state["clock"] = state["clock"] + 120
for record in expire_blocks(state, "INC-005"):
    append_log(record)
    print(
        record["incident"],
        record["target"],
        "·",
        record["before"],
        "→",
        record["after"],
        "·",
        record["reason"],
    )
print("차단한 IP:", state["blocked_ips"])

save_state(state)
print("--- 단계 4: 파일에 저장된 값 다시 읽기")
print("차단한 IP:", load_state()["blocked_ips"])
print("조치 기록:", len(load_json("containment_log.json")), "건")
