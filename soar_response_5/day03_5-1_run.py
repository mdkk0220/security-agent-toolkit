from incident import load_json
from containment_store import LOG_PATH, load_state
from ip_actions import block_ip, DEFAULT_TTL
from rollback import rollback_incident

state = load_state()
log = load_json(LOG_PATH)

print("--- 단계 1: 4교시가 남긴 파일")
print("잠긴 계정:", state["locked_users"])
print("조치 기록:", len(log), "건")
log.append(block_ip("198.51.100.90", state, "INC-005", "경로 스캔", DEFAULT_TTL))
print("차단한 IP:", state["blocked_ips"])

for incident_id, title in [
    ("INC-001", "단계 2: INC-001 은 오탐으로 확인됨 — 되돌리기"),
    ("INC-006", "단계 3: INC-006 도 오탐으로 확인됨 — 되돌리기"),
    ("INC-005", "단계 4: INC-005 도 오탐으로 확인됨 — 되돌리기"),
]:
    print("---", title)
    for record in rollback_incident(incident_id, log, state):
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

print("--- 단계 5: 되돌린 뒤 상태")
print("잠긴 계정:", state["locked_users"])
print("차단한 IP:", state["blocked_ips"])
