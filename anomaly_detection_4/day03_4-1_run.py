from classify import load_events, count_types, EVENTS_PATH, TYPE_ORDER

events = load_events(EVENTS_PATH)
counts = count_types(events)
print("--- 단계 1: 유형별 이벤트 수")
for type_name in TYPE_ORDER:
    count = counts.get(type_name, 0)
    print(type_name, count)

values = counts.values()
total = sum(values)
print("--- 단계 2: 전체 이벤트", total, "개")
