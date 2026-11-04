from req_create import REQUESTS, create_request
from req_review import approve_request, reject_request

INBOX = [
    ("seoyeon", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 대조 지원", "2026-10-23 08:30"),
    ("gaeun", "SALES", "QUERY", "2026-10-28 18:00", "감사 자료 대응", "2026-10-23 08:40"),
    ("dami", "SALES", "QUERY", "2026-10-27 18:00", "인수인계 자료 확인", "2026-10-23 08:50"),
    ("junho", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 확인", "2026-10-23 09:00"),
]
for request_data in INBOX:
    create_request(*request_data)

DECISIONS = [(1, "승인"), (2, "반려"), (3, "승인"), (4, "승인"), (1, "승인"), (2, "승인")]

print("--- 단계 1: 처리 - 본인 요청 시험 한 건, 승인 · 반려 여섯 건을 처리한다")
ok, result = approve_request(REQUESTS[0], "seoyeon")
print(1, "본인 승인 ->", ok, result)
for number, decision in DECISIONS:
    request = REQUESTS[number - 1]
    if decision == "승인":
        ok, result = approve_request(request, "security_manager")
    else:
        ok, result = reject_request(request, "security_manager")
    print(number, decision, "->", ok, result)

print("--- 단계 2: 점검 - 요청서 목록")
for request in REQUESTS:
    print(request["id"], request["user"], request["status"], request.get("approver"))
