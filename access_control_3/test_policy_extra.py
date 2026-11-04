from datetime import datetime

from policy import evaluate_access


def at(text):
    return datetime.strptime(text, "%Y-%m-%d %H:%M")


ok, reason = evaluate_access("dami", "SALES", "QUERY", at("2026-10-22 14:00"))
assert ok is False and reason == "퇴사한 계정", "5. 퇴사자는 예외가 있어도 거부"
print("5 통과")

ok, reason = evaluate_access("seoyeon", "SETTLE", "QUERY", at("2026-10-22 18:00"))
assert ok is True, "6. 만료 정각에도 허용되어야 한다(팀원 제안)"
print("6 통과")
