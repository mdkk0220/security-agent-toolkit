from access_detection import (
    EVENTS_PATH,
    load_events,
    pick_server_failures,
    pick_suspicious,
)
from malicious_detection import find_scan_ips, pick_web_failures
from saas_detection import (
    find_bulk_download_users,
    find_new_ip_users,
    find_off_hours_logins,
    pick_logins,
    pick_saas,
)

events = load_events(EVENTS_PATH)

server_failures = pick_server_failures(events)
suspicious = pick_suspicious(server_failures)
suspicious_count = len(suspicious)
print("판정 서버: 먼저 확인할 실패 이벤트", suspicious_count, "개")

saas = pick_saas(events)
logins = pick_logins(saas)
off_hours_logins = find_off_hours_logins(logins)
off_hours_users = list(off_hours_logins["user"])
new_ip_users = find_new_ip_users(logins)
bulk_users = find_bulk_download_users(saas)
print(
    "SaaS: 업무 시간 밖",
    off_hours_users,
    "· 평소와 다른 IP",
    new_ip_users,
    "· 대량 다운로드",
    bulk_users,
)

web_failures = pick_web_failures(events)
scan_ips, scan_counts = find_scan_ips(web_failures)
print("웹 서버: 스캔으로 본 IP", scan_ips)
