import json
from datetime import datetime

from exception_policy import EXCEPTIONS, TIME_FORMAT, find_exception

NOW = datetime.strptime("2026-10-22 14:00", TIME_FORMAT)
CHECKS = [
    ("seoyeon", "SETTLE:QUERY"),
    ("junho", "SALES:CHANGE"),
    ("dami", "SALES:QUERY"),
    ("batch-night", "SALES:QUERY"),
    ("gaeun", "SETTLE:QUERY"),
    ("seoyeon", "ACCOUNT:CHANGE"),
]

print("--- 단계 1: 판정 - 지금 유효한 예외가 있나")
for user, permission in CHECKS:
    print(user, permission, "->", find_exception(user, permission, NOW))

with open("config/users.json", encoding="utf-8") as file:
    USERS = json.load(file)

print("--- 단계 2: 점검 - 예외 목록에서 회수할 것")
for exception in EXCEPTIONS:
    expires = datetime.strptime(exception["expires"], TIME_FORMAT)
    if NOW >= expires:
        print("[회수] 만료됨", exception["id"], exception["user"], exception["permission"], exception["expires"])
    elif not USERS[exception["user"]]["employed"]:
        print("[회수] 퇴사자", exception["id"], exception["user"], exception["permission"], exception["expires"])
    else:
        print("[유지]", exception["id"], exception["user"], exception["permission"], exception["expires"])
