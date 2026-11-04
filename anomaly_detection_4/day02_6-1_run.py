import pandas as pd
from events_time import load_events, add_hour, pick_failed, count_by_user, count_by_hour, save_failed, EVENTS_PATH, FAILED_PATH

events = load_events(EVENTS_PATH)
events = add_hour(events)
failed = pick_failed(events)

by_user = count_by_user(failed)
print("--- 단계 1: 사용자별 실패 횟수")
print(by_user)

by_hour = count_by_hour(failed)
print("--- 단계 2: 시간대별 실패 횟수")
print(by_hour)

save_failed(failed, FAILED_PATH)
saved = pd.read_csv(FAILED_PATH)
saved_count = len(saved)
print("--- 단계 3: 저장한 파일", FAILED_PATH)
print("저장된 행", saved_count, "개")
