import sys

from incident import load_json, save_json
from false_positive import handle_false_positive, RECOVERY_LIMIT

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

NOW = 45

state = load_json("fp_state.json")
log = load_json("fp_log.json")
reports = load_json("fp_reports.json")
print("--- 단계 1: 오탐 신고", len(reports), "건 · 조치 기록", len(log), "건 · 지금", NOW, "분")
print("처리 전 잠긴 계정:", state["locked_users"], "· 차단된 IP:", state["blocked_ips"])

results = []
print("--- 단계 2: 신고마다 영향 확인 · 되돌리기 · 복구 확인 · 규칙 조정 제안")
for report in reports:
    result = handle_false_positive(report, log, state, NOW)
    results.append(result)
    print("[" + result["incident"] + "] 신고:", report["reporter"], "—", report["reason"])
    print(" - 영향 확인:", result["changed"])
    print(" - 되돌리기:", result["undone"])
    print(" - 복구 확인: 아직 잠기거나 차단된 대상", result["remaining"], "· 걸린 시간", result["minutes"], "분 · 기준", RECOVERY_LIMIT, "분 안", result["in_time"])
    print(" - 규칙 조정 제안:", result["tuning"])

print("--- 단계 3: 처리 뒤 상태 (오탐이 아닌 계정은 그대로인지)")
print("잠긴 계정:", state["locked_users"], "· 차단된 IP:", state["blocked_ips"])
print("dami 는 아직 잠김:", "dami" in state["locked_users"])

save_json(results, "fp_results.json")
save_json(state, "fp_state_after.json")
print("--- 단계 4: fp_results.json 에", len(results), "건 · fp_state_after.json 저장 · 기준", RECOVERY_LIMIT, "분")
