from traffic_detection import (
    EVENTS_PATH,
    SPIKE_MULTIPLE,
    TRAFFIC_PATH,
    add_minute_column,
    count_web_per_minute,
    load_events,
    make_traffic_limit,
    pick_spike_minutes,
)

events = load_events(EVENTS_PATH)
events = add_minute_column(events)
times = events["time"]
minutes = events["minute"]
first_times = times.head(3)
first_minutes = minutes.head(3)
print("--- 단계 1: time 열과 minute 열의 처음 3개 비교")
print(first_times)
print(first_minutes)

counts = count_web_per_minute(events)
print("--- 단계 2: 웹 서버의 분당 요청 수")
print(counts)

limit = make_traffic_limit(TRAFFIC_PATH, SPIKE_MULTIPLE)
print("--- 단계 3: 급증 기준(평소 평균의", SPIKE_MULTIPLE, "배)", limit, "번 이상")

spike_minutes = pick_spike_minutes(counts, limit)
print("--- 단계 4: 요청이 급증한 분")
print(spike_minutes)
