from normalize_web import normalize_web

events = []
fail_count = 0
with open("access_sample.log", encoding="utf-8") as log_file:
    for line in log_file:
        event = normalize_web(line)
        if event is None:
            fail_count = fail_count + 1
        else:
            events.append(event)

event_count = len(events)
print("--- 단계 1: 정규화한 이벤트", event_count, "개 · 읽기 실패", fail_count, "줄")
first_event = events[0]
print(first_event)

first_failed = None
for event in events:
    if event["result"] == "실패" and first_failed is None:
        first_failed = event
print("--- 단계 2: 처음 나오는 실패 이벤트")
print(first_failed)

counts = {}
for event in events:
    result = event["result"]
    counts[result] = counts.get(result, 0) + 1
print("--- 단계 3: 성공 · 실패별 개수")
print(counts)
