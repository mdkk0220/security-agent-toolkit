import sys

from incident import INCIDENTS_PATH, load_json
from enrichment import enrich_incident

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

incidents = load_json(INCIDENTS_PATH)
users_info = load_json("users_info.json")
source_ips = load_json("source_ips.json")
trusted_ips = load_json("trusted_ips.json")
incident_count = len(incidents)
user_count = len(users_info)
trusted_count = len(trusted_ips)
print("--- 단계 1: 불러온 알림", incident_count, "건 · 계정 정보", user_count, "명 · 신뢰 IP", trusted_count, "개")

print("--- 단계 2: 알림마다 붙인 정보(재직 · VIP · 접속 IP)")
for incident in incidents:
    enrich_incident(incident, users_info, source_ips, trusted_ips)
    context = incident["context"]
    if context["account_known"]:
        if context["employed"]:
            employed_text = "재직"
        else:
            employed_text = "퇴사"
    else:
        employed_text = "계정 아님"
    vip_text = "아니오"
    if context["vip"]:
        vip_text = "예"
    ip_text = "없음"
    if context["source_ip"]:
        ip_text = context["source_ip"]
    trusted_text = "아니오"
    if context["ip_trusted"]:
        trusted_text = "예"
    print(
        incident["id"],
        incident["entity"],
        "· 재직:",
        employed_text,
        "· VIP:",
        vip_text,
        "· 접속 IP:",
        ip_text,
        "· 신뢰 IP:",
        trusted_text,
    )

print("--- 단계 3: VIP 계정 알림 수")
vip_count = 0
for incident in incidents:
    context = incident["context"]
    if context["vip"]:
        vip_count = vip_count + 1
print("VIP 계정 알림", vip_count, "건")
