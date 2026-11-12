from incident import load_json
from containment_store import (
    append_log,
    load_state,
    new_state,
    reset_log,
    save_state,
)
from session_actions import find_open_sessions
from containment import contain_account

vip_accounts = load_json("config/vip_accounts.json")
requests = [
    ("INC-001", "dami", "퇴사한 계정의 서버 요청"),
    ("INC-003", "gaeun", "여러 로그 연결"),
    ("INC-006", "junho", "퇴사 처리 확인"),
]
state = new_state()
reset_log()

print("--- 단계 1: 점검 - 잠겼는데 세션이 열려 있는 계정")
print(find_open_sessions(state))

print("--- 단계 2: 잠금 → 세션 종료")
for incident_id, user, reason in requests:
    records = contain_account(user, state, vip_accounts, incident_id, reason)
    for record in records:
        append_log(record)
        print(
            record["incident"],
            record["target"],
            "·",
            record["before"],
            "→",
            record["after"],
            "·",
            record["reason"],
        )

print("--- 단계 3: 조치 뒤 다시 점검")
gaps_after = find_open_sessions(state)
print("빈틈이 남은 계정:", gaps_after)
print("잠긴 계정:", state["locked_users"])

save_state(state)
print("--- 단계 4: 파일에 저장된 값 다시 읽기")
print("잠긴 계정:", load_state()["locked_users"])
print("조치 기록:", len(load_json("containment_log.json")), "건")
