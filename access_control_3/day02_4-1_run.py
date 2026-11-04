from datetime import datetime

from exception_policy import EXCEPTIONS
from policy import evaluate_access

TODAY_LOG = [
    ("09:10", "seoyeon", "SETTLE", "QUERY"),
    ("10:00", "dami", "SALES", "QUERY"),
    ("11:40", "gaeun", "SETTLE", "QUERY"),
    ("12:30", "gaeun", "SETTLE", "QUERY"),
    ("13:00", "junho", "SETTLE", "QUERY"),
    ("14:00", "batch-night", "SALES", "QUERY"),
    ("15:00", "junho", "SALES", "CHANGE"),
    ("16:20", "seoyeon", "SETTLE", "QUERY"),
    ("18:05", "seoyeon", "SETTLE", "QUERY"),
]

counts = {}
used = {}
for time, user, resource, action in TODAY_LOG:
    now = datetime.strptime("2026-10-22 " + time, "%Y-%m-%d %H:%M")
    ok, reason = evaluate_access(user, resource, action, now)
    print(time, user, resource, action, "->", ok, reason)
    if ok and reason == "역할 권한":
        counts["역할로 허용"] = counts.get("역할로 허용", 0) + 1
    elif ok:
        counts["예외로 허용"] = counts.get("예외로 허용", 0) + 1
        used[reason] = used.get(reason, 0) + 1
    else:
        counts["거부"] = counts.get("거부", 0) + 1
        if reason == "권한 없음":
            for exception in EXCEPTIONS:
                if exception["user"] == user and exception["permission"] == resource + ":" + action:
                    print("[만료 뒤 시도]", time, user, resource, action, "- 만료된 예외", exception["id"], exception["expires"])

print(counts)
print("예외 사용", used)
