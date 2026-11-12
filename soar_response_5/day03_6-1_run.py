from incident import load_json, save_json, INCIDENTS_PATH
from containment_store import new_state
from drill import handle_incident
from shift_report import summarize, is_failure

extra_incidents = [
    {
        "id": "INC-008",
        "entity": "192.0.2.41",
        "grade": "low",
        "score": 30,
        "reasons": ["경로 스캔"],
        "status": "탐지됨",
    },
    {
        "id": "INC-009",
        "entity": "192.0.2.10",
        "grade": "low",
        "score": 30,
        "reasons": ["경로 스캔"],
        "status": "탐지됨",
    },
    {
        "id": "INC-010",
        "entity": "gaeun",
        "grade": "high",
        "score": 60,
        "reasons": ["퇴사한 계정"],
        "status": "탐지됨",
    },
]
incidents = load_json(INCIDENTS_PATH) + extra_incidents
refs = {
    "users_info": load_json("users_info.json"),
    "source_ips": load_json("source_ips.json"),
    "trusted_ips": load_json("trusted_ips.json"),
    "vip_accounts": load_json("config/vip_accounts.json"),
    "allowlist_ips": load_json("config/allowlist_ips.json"),
    "ip_users": load_json("ip_users.json"),
}
state = new_state()
log = []
statuses = {}

print("--- 단계 1: 알림 8건 처리")
for incident in incidents:
    status, records = handle_incident(incident, state, refs)
    statuses[incident["id"]] = status
    for record in records:
        log.append(record)
    print(incident["id"], incident["entity"], "->", status, "(조치 기록 " + str(len(records)) + "건)")

save_json(log, "shift_log.json")
print("--- 단계 2: 조치 기록")
for record in log:
    print(
        record["incident"],
        record["target"],
        "·",
        record["action"],
        "·",
        record["before"],
        "→",
        record["after"],
        "·",
        record["reason"],
    )

print("--- 단계 3: 근무 보고 요약")
print(summarize(log))
print("잠긴 계정:", state["locked_users"])
print("차단한 IP:", state["blocked_ips"])

print("--- 단계 4: 담당자 확인이 필요한 건")
for incident in incidents:
    if statuses[incident["id"]] == "승인 대기" and incident["context"]["vip"]:
        print(incident["id"], incident["entity"], ": VIP 계정이라 담당자 승인이 필요함")
for record in log:
    if "승인 필요" in record["reason"]:
        print(record["incident"], record["target"], ":", record["reason"])
    if is_failure(record):
        print(record["incident"], record["target"], ": 조치 후 확인 실패 —", record["reason"])
