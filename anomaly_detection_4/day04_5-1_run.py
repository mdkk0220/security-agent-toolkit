from access_detection import EVENTS_PATH, load_events, pick_server_failures
from correlation import (
    WINDOW_MINUTES,
    attach_user_to_web,
    build_timeline,
    find_chains,
    make_ip_user_map,
)
from malicious_detection import pick_web_failures
from saas_detection import pick_logins, pick_saas

events = load_events(EVENTS_PATH)
server_part = pick_server_failures(events)
saas_part = pick_saas(events)
logins = pick_logins(saas_part)
ip_user = make_ip_user_map(logins)

web_failures = pick_web_failures(events)
web_part = attach_user_to_web(web_failures, ip_user)
print("--- 단계 1: IP 로 사용자를 알 수 있는 웹 실패 이벤트", len(web_part), "개")

timeline = build_timeline(server_part, saas_part, web_part)
print("--- 단계 2: 사용자별로 시간순으로 놓은 이벤트", len(timeline), "개")
print("gaeun 의 이벤트 (시각 · 로그 · 행동 · 결과)")
for event in timeline[timeline["user"] == "gaeun"].to_dict("records"):
    print(event["time"], event["source"], event["action"], event["result"])

chains, not_chained = find_chains(timeline)
print("--- 단계 3:", WINDOW_MINUTES, "분 안에 서로 다른 로그로 연결된 사건")
for chain in chains:
    print(chain)

print("--- 단계 4: 로그 종류는 여럿이지만 시간 차가 60분을 초과해 연결되지 않은 사용자")
for item in not_chained:
    print(item)
