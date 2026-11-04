from req_create import REQUESTS, create_request

INBOX = [
    ("seoyeon", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 대조 지원", "2026-10-23 08:30"),
    ("gaeun", "SALES", "QUERY", "2026-10-28 18:00", "감사 자료 대응", "2026-10-23 08:40"),
    ("dami", "SALES", "QUERY", "2026-10-27 18:00", "인수인계 자료 확인", "2026-10-23 08:50"),
    ("junho", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 확인", "2026-10-23 09:00"),
    ("hana", "SALES", "QUERY", "2026-10-27 18:00", "신규 업무 지원", "2026-10-23 09:05"),
    ("seoyeon", "ACCOUNT", "QUERY", "2026-10-27 18:00", "", "2026-10-23 09:10"),
    ("gaeun", "ACCOUNT", "QUERY", "2026-10-22 18:00", "어제 적은 요청서 재사용", "2026-10-23 09:15"),
]

print("--- 단계 1: 접수 - 요청 일곱 건을 하나씩 넣는다")
for user, resource, action, until, reason, received_at in INBOX:
    ok, result = create_request(user, resource, action, until, reason, received_at)
    if ok:
        print(user, resource, action, "-> 접수됨, 요청 번호", result["id"])
    else:
        print(user, resource, action, "-> 접수 안 됨:", result)

print("--- 단계 2: 점검 - 요청서 목록")
for request in REQUESTS:
    print(request["id"], request["user"], request["permission"], request["status"])
