import sys

from approvals import apply_decision
from failure_report import collect_failures
from flow import run_day_flow
from incident import INCIDENTS_PATH, load_json
from retry_runner import MAX_TRIES, run_with_retry

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def new_state():
    state = {"locked_users": [], "blocked_ips": [], "tickets": [], "notifications": []}
    return state


incidents = load_json(INCIDENTS_PATH)
users_info = load_json("users_info.json")
source_ips = load_json("source_ips.json")
trusted_ips = load_json("trusted_ips.json")
registry = load_json("config/playbook_registry.json")
decisions = load_json("decisions.json")

print("--- 단계 1: 일시 장애 — 티켓 서비스가 2번 실패한 뒤 복구")
state = new_state()
fail_plan = {"INC-001|티켓 생성": 2}
result = run_with_retry("티켓 생성", incidents[0], state, fail_plan, MAX_TRIES)
print(result)
print("만든 티켓:", len(state["tickets"]), "건")

print("--- 단계 2: 서비스 중단 — 티켓 서비스가 계속 실패")
state = new_state()
fail_plan = {"INC-001|티켓 생성": 99}
result = run_with_retry("티켓 생성", incidents[0], state, fail_plan, MAX_TRIES)
print(result)
print("만든 티켓:", len(state["tickets"]), "건")

print("--- 단계 3: 하루 흐름 — 티켓 서비스가 계속 실패하는 상황")
state = new_state()
action_log = []
fail_plan = {"INC-001|티켓 생성": 99}
pending = run_day_flow(
    incidents,
    registry,
    users_info,
    source_ips,
    trusted_ips,
    state,
    action_log,
    fail_plan,
)

print("--- 단계 4: 담당자 결정 처리")
for item in pending:
    result_text = apply_decision(item, decisions[item["id"]], state, action_log)
    print(item["id"], item["entity"], "->", result_text, "(상태: " + item["status"] + ")")

print("--- 단계 5: 하루가 끝난 뒤 모의 시스템 상태")
print("잠긴 계정:", state["locked_users"])
print("차단한 IP:", state["blocked_ips"])
print("티켓:", len(state["tickets"]), "건 · 담당자 알림:", len(state["notifications"]), "건")

print("--- 단계 6: 담당자 확인이 필요한 건")
failures = collect_failures(action_log)
for entry in failures:
    incident_id = entry["incident"]
    print(incident_id, entry["action"], ":", entry["result"])
for item in pending:
    if item["status"] == "분류됨":
        print(item["id"], "승인 대기 :", item["why"])
