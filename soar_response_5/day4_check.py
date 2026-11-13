from report import find_missing_incidents
from approval_gate import decide_gate


def check_report(report_text, tickets, actions):
    expected = []
    for ticket in tickets:
        expected.append(ticket["id"])
    for action in find_missing_incidents(actions, tickets):
        expected.append(action["incident"])
    not_found = []
    for number in expected:
        if number not in report_text:
            not_found.append(number)
    return not_found


def check_gate(cases, policy):
    wrong = []
    for case in cases:
        decision, reasons = decide_gate(case["request"], policy)
        if decision != case["expected"]:
            wrong.append(case["case"] + " (기대 " + case["expected"] + ", 결과 " + decision + ")")
    return wrong


def check_recovery(results, state, true_positive_users):
    problems = []
    for result in results:
        if result["remaining"] != []:
            problems.append(result["incident"] + " 복구 안 됨")
        if not result["in_time"]:
            problems.append(result["incident"] + " 30분 넘음")
    for user in true_positive_users:
        if user not in state["locked_users"]:
            problems.append(user + " 잠금이 풀림")
    return problems


def mark(problems):
    if problems == []:
        return "통과"
    return "확인 필요"
