from datetime import datetime
from conditional import load_rules, evaluate_conditional

TIME_FORMAT = "%Y-%m-%d %H:%M"
RULES = load_rules("config/conditions.json")

CASES = [
    ("seoyeon", "SALES", "QUERY", "office", "2026-10-30 10:00"),
    ("seoyeon", "SALES", "CHANGE", "office", "2026-10-30 09:00"),
    ("seoyeon", "SALES", "CHANGE", "office", "2026-10-30 18:00"),
    ("seoyeon", "SALES", "CHANGE", "external", "2026-10-30 10:00"),
    ("seoyeon", "SALES", "CHANGE", "external", "2026-10-30 22:00"),
    ("junho", "SETTLE", "QUERY", "vpn", "2026-10-30 19:30"),
    ("gaeun", "ACCOUNT", "CHANGE", "vpn", "2026-10-30 10:00"),
    ("dami", "SALES", "QUERY", "office", "2026-10-30 10:00"),
]

print("--- 단계 1: 판정 - 요청", len(CASES), "건")
for number, (user, resource, action, network, time_text) in enumerate(CASES, 1):
    now = datetime.strptime(time_text, TIME_FORMAT)
    ok, reason = evaluate_conditional(user, resource, action, network, now, RULES)
    result = "허용" if ok else "거부"
    permission = f"{resource}:{action}"
    print(number, user, permission, network, now.strftime("%H:%M"), "->", f"{result}({reason})")

print("--- 단계 2: 확인 - 조건 파일에 적힌 조건")
for rule in RULES:
    hours = rule["hours"]
    hours_text = f"{hours[0]}시부터 {hours[1]}시 전까지"
    networks_text = ", ".join(rule["networks"])
    print(rule["permission"], "|", hours_text, "|", networks_text)