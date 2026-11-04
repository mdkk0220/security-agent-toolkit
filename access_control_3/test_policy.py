from datetime import datetime

from config_loader import load_json
from policy import evaluate_access


def at(text):
    return datetime.strptime(text, "%Y-%m-%d %H:%M")


ok, reason = evaluate_access("junho", "SETTLE", "QUERY", at("2026-10-22 14:00"))
assert ok is True and reason == "역할 권한", "1. 정상 허용"

ok, reason = evaluate_access("seoyeon", "ACCOUNT", "CHANGE", at("2026-10-22 14:00"))
assert ok is False and reason == "권한 없음", "2. 권한 없음"

ok, reason = evaluate_access("seoyeon", "SETTLE", "QUERY", at("2026-10-22 17:59"))
assert ok is True and reason == "예외 1번", "3-1. 만료 1분 전 허용"
ok, reason = evaluate_access("seoyeon", "SETTLE", "QUERY", at("2026-10-22 18:00"))
assert ok is False, "3-2. 만료 정각 거부"

users = load_json("config/no_such.json", {})
assert "seoyeon" not in users, "4. 설정 고장이면 사용자 없음"

print("테스트 4개 모두 통과")
