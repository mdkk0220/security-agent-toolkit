from baseline import load_daily_failures, average_failures, maximum_failures, make_limit, LOGIN_PATH

daily = load_daily_failures(LOGIN_PATH)
print("--- 단계 1: 지난 7일 하루 로그인 실패 횟수")
print(daily)

average = average_failures(daily)
rounded_average = round(average, 1)
print("--- 단계 2: 하루 평균", rounded_average, "번")

maximum = maximum_failures(daily)
print("--- 단계 3: 하루 최대", maximum, "번")

limit = make_limit(maximum)
print("--- 단계 4: 알림 기준(임계값)", limit, "번 이상")
