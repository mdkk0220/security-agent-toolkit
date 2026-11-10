from incident import (
    INCIDENTS_PATH,
    LOG_PATH,
    REGISTRY_PATH,
    STATE_PATH,
    load_json,
    save_json,
)
from playbook_runner import process_incidents

incidents = load_json(INCIDENTS_PATH)
registry = load_json(REGISTRY_PATH)
incident_count = len(incidents)
playbook_count = len(registry)
print("--- 단계 1: 불러온 인시던트", incident_count, "건 · 등록된 플레이북", playbook_count, "개")

state = {"locked_users": [], "blocked_ips": [], "tickets": [], "notifications": []}
action_log = []
print("--- 단계 2: 실행 전 모의 시스템 상태")
print("잠긴 계정:", state["locked_users"])
print("차단한 IP:", state["blocked_ips"])
print("티켓:", len(state["tickets"]), "건 · 담당자 알림:", len(state["notifications"]), "건")

print("--- 단계 3: 인시던트마다 플레이북 실행")
pending = process_incidents(incidents, registry, state, action_log)

print("--- 단계 4: 실행 후 모의 시스템 상태")
print("잠긴 계정:", state["locked_users"])
print("차단한 IP:", state["blocked_ips"])
print("티켓:", len(state["tickets"]), "건 · 담당자 알림:", len(state["notifications"]), "건")

pending_count = len(pending)
print("--- 단계 5: 승인 대기", pending_count, "건")
for waiting in pending:
    print(waiting["incident"], waiting["entity"], waiting["playbook"], "·", waiting["approval"])

save_json(state, STATE_PATH)
save_json(action_log, LOG_PATH)
log_count = len(action_log)
print("--- 단계 6: 감사 기록", log_count, "건을", LOG_PATH, "에 저장")
for entry in action_log:
    print(entry["incident"], entry["playbook"], entry["action"], ":", entry["result"])
