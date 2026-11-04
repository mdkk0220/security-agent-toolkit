from datetime import datetime

from policy import evaluate_access
from req_create import REQUESTS, create_request
from req_grant import grant_request
from req_review import approve_request, reject_request

NOW = datetime.strptime("2026-10-23 10:00", "%Y-%m-%d %H:%M")
INBOX = [
    ("seoyeon", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 대조 지원", "2026-10-23 08:30"),
    ("gaeun", "SALES", "QUERY", "2026-10-28 18:00", "감사 자료 대응", "2026-10-23 08:40"),
    ("dami", "SALES", "QUERY", "2026-10-27 18:00", "인수인계 자료 확인", "2026-10-23 08:50"),
    ("junho", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 확인", "2026-10-23 09:00"),
]
for request_data in INBOX:
    create_request(*request_data)
for number in [1, 3, 4]:
    approve_request(REQUESTS[number - 1], "security_manager")
reject_request(REQUESTS[1], "security_manager")


def show(title):
    print("---", title)
    for request in REQUESTS:
        ok, reason = evaluate_access(request["user"], request["resource"], request["action"], NOW)
        print(request["id"], request["user"], request["permission"], "->", ok, reason)


show("단계 1: 판정 - 부여 전")
print("--- 단계 2: 부여 - 요청서마다 부여를 시도한다")
for request in REQUESTS:
    ok, result = grant_request(request)
    print(request["id"], request["user"], request["status"], "->", ok, result)
for request in REQUESTS:
    if "exception_id" in request:
        print("부여된 예외 번호:", request["exception_id"])
show("단계 3: 점검 - 부여 후")
