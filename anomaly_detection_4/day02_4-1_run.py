from normalize import load_web, merge_events, count_by_source, count_missing, save_events, EVENTS_PATH
from normalize_json_csv import load_server, load_saas
import json


def show_user(events, name):
    """Print one user's events in time order."""
    for event in events:
        if event["user"] == name:
            time_text = event["time"]
            source = event["source"]
            action = event["action"]
            result = event["result"]
            print(time_text, source, action, result)


web = load_web("access_sample.log")
server = load_server("server_log.jsonl")
saas = load_saas("saas_events.csv")
events = merge_events(web, server, saas)

source_counts = count_by_source(events)
print("--- 단계 1: 소스별 이벤트 수")
print(source_counts)

user_missing = count_missing(events, "user")
ip_missing = count_missing(events, "ip")
print("--- 단계 2: 값이 None 인 이벤트 수")
print("user 가 비어 있는 이벤트", user_missing, "개")
print("ip 가 비어 있는 이벤트", ip_missing, "개")

print("--- 단계 3: gaeun 의 이벤트를 시간순으로")
show_user(events, "gaeun")

save_events(events, EVENTS_PATH)
with open(EVENTS_PATH, encoding="utf-8") as events_file:
    saved_events = json.load(events_file)
saved_count = len(saved_events)
print("--- 단계 4: 저장한 파일", EVENTS_PATH)
print("저장된 이벤트", saved_count, "개")
