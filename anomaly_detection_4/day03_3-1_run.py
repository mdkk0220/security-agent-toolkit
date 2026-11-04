from login_detection import load_events, pick_login_failures, count_by_ip, pick_alert_ips, EVENTS_PATH, LOGIN_LIMIT

events = load_events(EVENTS_PATH)
login_failures = pick_login_failures(events)
failure_count = len(login_failures)
print("--- 단계 1: 로그인 실패 이벤트", failure_count, "개")

counts = count_by_ip(login_failures)
print("--- 단계 2: 주소별 로그인 실패 횟수")
print(counts)

alert_ips = pick_alert_ips(counts, LOGIN_LIMIT)
print("--- 단계 3: 알림 기준", LOGIN_LIMIT, "번 이상인 주소")
print(alert_ips)
