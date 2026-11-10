import sys

from approvals import apply_decision
from incident import load_json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

pending = load_json("pending.json")
decisions = load_json("decisions.json")
state = {"locked_users": [], "blocked_ips": [], "tickets": [], "notifications": []}
action_log = []

print("--- 단계 1: 승인 대기 건")
for item in pending:
    print(item["id"], item["entity"], "·", item["playbook"], "·", item["why"])

print("--- 단계 2: 담당자 결정 처리")
for item in pending:
    result_text = "결정 없음"
    if item["id"] in decisions:
        result_text = apply_decision(item, decisions[item["id"]], state, action_log)
    print(item["id"], item["entity"], "->", result_text, "(상태: " + item["status"] + ")")

print("--- 단계 3: 처리 뒤 모의 시스템 상태")
print("잠긴 계정:", state["locked_users"])
print("차단한 IP:", state["blocked_ips"])
print("티켓:", len(state["tickets"]), "건 · 담당자 알림:", len(state["notifications"]), "건")

print("--- 단계 4: 감사 기록")
for entry in action_log:
    print(entry["incident"], entry["playbook"], entry["action"], ":", entry["result"])
