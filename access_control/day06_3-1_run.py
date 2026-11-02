import json

from log_summary import count_by, deny_rate, filter_denied, find_heavy_users, read_log

LOG_PATH = "week_log.jsonl"
with open("config/alert.json", encoding="utf-8") as alert_file:
    ALERT = json.load(alert_file)

entries = read_log(LOG_PATH)
denied = filter_denied(entries)
rate = deny_rate(entries)
percent = round(rate * 100)
limit = ALERT["deny_rate_limit"]
limit_percent = round(limit * 100)
user_limit = ALERT["user_denied_limit"]

entry_count = len(entries)
print("--- 단계 1: 집계 - 요청", entry_count, "건")
denied_count = len(denied)
allowed_count = entry_count - denied_count
print("허용", allowed_count, "· 거부", denied_count, "· 거부율", f"{percent}%")
print("--- 단계 2: 거부 사유별")
reason_counts = count_by(denied, "reason")
for reason, count in reason_counts.items():
    print(reason, count)
print("--- 단계 3: 경고 기준")
if rate >= limit:
    print(f"거부율 {percent}% >= 기준 {limit_percent}% -> 경고")
else:
    print(f"거부율 {percent}% < 기준 {limit_percent}% -> 경고 없음")
user_counts = count_by(denied, "user")
heavy = find_heavy_users(user_counts, user_limit)
print("거부", user_limit, "번 이상 사용자:", heavy)
