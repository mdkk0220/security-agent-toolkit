from access_detection import (
    EVENTS_PATH,
    judge_failure,
    load_events,
    pick_server_failures,
    pick_suspicious,
)

LABELS = {
    "퇴사한 계정": "퇴사한 계정",
    "권한 없음": "권한 없음",
    "허용": "규칙은 허용인데 서버가 거절",
}

events = load_events(EVENTS_PATH)
server_failures = pick_server_failures(events)
failure_count = len(server_failures)
print("--- 단계 1: 판정 서버의 실패 이벤트", failure_count, "개")

suspicious = pick_suspicious(server_failures)
suspicious_count = len(suspicious)
print("--- 단계 2: 먼저 확인할 실패 이벤트", suspicious_count, "개")

suspicious_list = suspicious.to_dict("records")
judged_list = []
for event in suspicious_list:
    reason, priority = judge_failure(event["user"], event["action"])
    judged = {"priority": priority, "reason": reason, "event": event}
    judged_list.append(judged)

print("--- 단계 3: 우선순위")
priorities = sorted({item["priority"] for item in judged_list})
for priority in priorities:
    for judged in judged_list:
        if judged["priority"] == priority:
            event = judged["event"]
            label = LABELS.get(judged["reason"], judged["reason"])
            print(priority, label, event["user"], event["action"], event["time"])
