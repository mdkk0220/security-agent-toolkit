from incident import load_json
from containment_store import (
    append_log,
    load_state,
    make_record,
    new_state,
    reset_log,
    save_state,
)
from account_actions import lock_account, unlock_account

vip_accounts = load_json("config/vip_accounts.json")
requests = [
    ("INC-001", "dami", "퇴사한 계정의 서버 요청"),
    ("INC-003", "gaeun", "여러 로그 연결"),
    ("INC-006", "junho", "퇴사 처리 확인"),
]
state = new_state()
reset_log()

print("--- 단계 1: 조치 전에 잠겨 있는 계정")
print(state["locked_users"])

print("--- 단계 2: 잠금 요청 3건")
for incident_id, user, reason in requests:
    record = lock_account(user, state, vip_accounts, incident_id, reason)
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

print("--- 단계 3: 오탐으로 확인되어 dami 해제")
record = unlock_account("dami", state, "INC-001", "오탐으로 확인되어 해제")
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

save_state(state)
print("--- 단계 4: 파일에 저장된 값 다시 읽기")
saved_state = load_state()
saved_log = load_json("containment_log.json")
print("잠긴 계정:", saved_state["locked_users"])
print("조치 기록:", len(saved_log), "건")
