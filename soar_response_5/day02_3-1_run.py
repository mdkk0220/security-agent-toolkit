import sys

from incident import INCIDENTS_PATH, load_json
from enrichment import enrich_incident
from routing import apply_route, decide_route

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

incidents = load_json(INCIDENTS_PATH)
users_info = load_json("users_info.json")
source_ips = load_json("source_ips.json")
trusted_ips = load_json("trusted_ips.json")
incident_log = []
route_counts = {"기본": 0, "승인 필요": 0, "오탐 종료": 0}

print("--- 단계 1: 알림마다 정한 처리 경로 · 이유 · 상태")
for incident in incidents:
    enrich_incident(incident, users_info, source_ips, trusted_ips)
    route, reason = decide_route(incident)
    apply_route(incident, route, reason, incident_log)
    route_counts[route] = route_counts[route] + 1
    print(
        incident["id"],
        incident["entity"],
        incident["grade"],
        "->",
        route,
        "·",
        reason,
        "(상태: " + incident["status"] + ")",
    )

print("--- 단계 2: 경로별 건수")
for route in route_counts:
    print(route, route_counts[route], "건")
