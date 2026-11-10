import sys

from incident import (
    INCIDENTS_PATH,
    REGISTRY_PATH,
    load_json,
    match_playbooks,
)
from playbook_runner import run_playbook
from safe_runner import MAX_LOCKS_PER_RUN, process_safe

BULK_PATH = "bulk_incidents.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def new_state():
    state = {
        "locked_users": [],
        "blocked_ips": [],
        "tickets": [],
        "notifications": [],
    }
    return state


def run_monday_way(incidents, registry, state, action_log):
    for incident in incidents:
        playbooks = match_playbooks(incident, registry)
        for playbook in playbooks:
            run_playbook(incident, playbook, state, action_log)


registry = load_json(REGISTRY_PATH)

print("--- 단계 1: 어제 방식(안전장치 없음)으로 같은 알림 5건을 두 번 처리")
incidents = load_json(INCIDENTS_PATH)
state = new_state()
action_log = []
run_monday_way(incidents, registry, state, action_log)
run_monday_way(incidents, registry, state, action_log)
print("잠긴 계정:", state["locked_users"])
print("티켓:", len(state["tickets"]), "건")

print("--- 단계 2: 어제 방식(안전장치 없음)으로 인사 오류 알림 7건 처리")
bulk_incidents = load_json(BULK_PATH)
state = new_state()
action_log = []
run_monday_way(bulk_incidents, registry, state, action_log)
locked_count = len(state["locked_users"])
print("잠긴 계정", locked_count, "개:", state["locked_users"])

print("--- 단계 3: 안전한 방식으로 같은 알림 5건을 두 번 처리")
incidents = load_json(INCIDENTS_PATH)
state = new_state()
action_log = []
print("첫 번째 처리")
process_safe(incidents, registry, state, action_log)
print("두 번째 처리")
process_safe(incidents, registry, state, action_log)
print("잠긴 계정:", state["locked_users"])
print("티켓:", len(state["tickets"]), "건")

print(
    "--- 단계 4: 안전한 방식으로 인사 오류 알림 7건 처리 (한 번에 최대",
    MAX_LOCKS_PER_RUN,
    "개)",
)
bulk_incidents = load_json(BULK_PATH)
state = new_state()
action_log = []
counts = process_safe(bulk_incidents, registry, state, action_log)
locked_count = len(state["locked_users"])
print("잠긴 계정", locked_count, "개:", state["locked_users"])
print("결과별 건수:", counts)
print("티켓:", len(state["tickets"]), "건")
print("건너뛴 액션과 이유:")
for entry in action_log:
    result_text = entry["result"]
    if result_text.startswith("건너뜀"):
        print(entry["incident"], entry["action"], "->", result_text)
