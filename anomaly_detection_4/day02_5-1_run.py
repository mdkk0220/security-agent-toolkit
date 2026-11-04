from events_basic import load_events, describe_events, pick_failed, count_values, EVENTS_PATH

events = load_events(EVENTS_PATH)
shape, first_times = describe_events(events)
print("--- 단계 1: 표 크기(행 수, 열 수)와 처음 3개 시각")
print(shape)
for time_text in first_times:
    print(time_text)

result_counts = count_values(events, "result")
print("--- 단계 2: 성공 · 실패별 개수")
print(result_counts)

failed = pick_failed(events)
failed_count = len(failed)
source_counts = count_values(failed, "source")
print("--- 단계 3: 실패한 이벤트", failed_count, "개의 소스별 개수")
print(source_counts)

all_source_counts = count_values(events, "source")
print("--- 단계 4: 전체 이벤트의 소스별 개수")
print(all_source_counts)
