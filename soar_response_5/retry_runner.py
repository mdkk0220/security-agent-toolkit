from safe_runner import safe_run_action

MAX_TRIES = 3


def flaky_run_action(action, incident, state, fail_plan):
    key = incident["id"] + "|" + action
    remaining = fail_plan.get(key, 0)
    if remaining > 0:
        fail_plan[key] = remaining - 1
        raise ConnectionError("연결 실패: " + action + " 서비스가 응답하지 않음")
    return safe_run_action(action, incident, state)


def run_with_retry(action, incident, state, fail_plan, max_tries):
    last_error = ""
    for attempt in range(1, max_tries + 1):
        try:
            result = flaky_run_action(action, incident, state, fail_plan)
            return result + " (시도 " + str(attempt) + "회)"
        except ConnectionError as error:
            last_error = str(error)
    return "실패: " + last_error + " (" + str(max_tries) + "회 모두 실패)"
