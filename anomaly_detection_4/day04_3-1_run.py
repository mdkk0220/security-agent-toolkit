from saas_detection import (
    EVENTS_PATH,
    find_bulk_download_users,
    find_new_ip_users,
    find_off_hours_logins,
    load_events,
    pick_logins,
    pick_saas,
)

events = load_events(EVENTS_PATH)
saas = pick_saas(events)
logins = pick_logins(saas)

off_hours_logins = find_off_hours_logins(logins)
off_hours_count = len(off_hours_logins)
print("--- 단계 1: 업무 시간 밖 로그인", off_hours_count, "건")
print(off_hours_logins)

new_ip_users = find_new_ip_users(logins)
print("--- 단계 2: 평소와 다른 IP 로 로그인한 사용자", new_ip_users)

bulk_users = find_bulk_download_users(saas)
print("--- 단계 3: 파일을 5번 이상 내려받은 사용자", bulk_users)
