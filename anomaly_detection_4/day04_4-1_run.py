from malicious_detection import (
    EVENTS_PATH,
    explain_scan,
    find_scan_ips,
    load_events,
    pick_web_failures,
)

events = load_events(EVENTS_PATH)
web_failures = pick_web_failures(events)
web_failure_count = len(web_failures)
print("--- 단계 1: 웹 서버의 실패 이벤트", web_failure_count, "개")

scan_ips, scan_counts = find_scan_ips(web_failures)
print("--- 단계 2: 스캐너 경로를 요청한 IP 와 횟수")
print(scan_counts)

print("--- 단계 3: 스캔으로 본 IP 와 이유")
for ip in scan_ips:
    request_count = scan_counts[ip]
    scan_info = explain_scan(ip, request_count)
    print(scan_info)

print("--- 단계 4: 스캐너 경로가 없어 제외한 IP")
all_ips = web_failures["ip"].unique()
for ip in all_ips:
    if ip not in scan_ips:
        print(ip)
