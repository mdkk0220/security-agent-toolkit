import sys

from incident import load_json, save_json
from approval_gate import decide_gate

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

policy = load_json("config/approval_policy.json")
requests = load_json("gate_requests.json")
print("--- 단계 1: 불러온 조치 요청", len(requests), "건 · 승인 기준", policy["approval_score"], "점")

counts = {"자동": 0, "승인 필요": 0, "차단 금지": 0}
results = []
print("--- 단계 2: 요청마다 결정과 이유")
for request in requests:
    decision, reasons = decide_gate(request, policy)
    counts[decision] = counts[decision] + 1
    reason_text = ", ".join(reasons)
    print(request["id"], request["action"], request["target"], "→", decision, "·", reason_text)
    results.append({"id": request["id"], "incident": request["incident"], "action": request["action"], "target": request["target"], "decision": decision})

print("--- 단계 3: 결정별 요청 수")
for decision in counts:
    print(decision, ":", counts[decision], "건")

print("--- 단계 4: 담당자에게 보낼 승인 요청")
for result in results:
    if result["decision"] == "승인 필요":
        print(result["id"], result["incident"], result["action"], result["target"], "→ 담당자 승인을 기다림")

save_json(results, "gate_results.json")
print("--- 단계 5: gate_results.json 에", len(results), "건 저장")
