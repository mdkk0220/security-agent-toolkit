import json
from datetime import datetime

TIME_FORMAT = "%Y-%m-%d %H:%M"


def load_state(path):
    with open(path, encoding="utf-8") as json_file:
        return json.load(json_file)


def check_employed(users):
    problems = []
    for name, info in users.items():
        if not info["employed"]:
            problems.append(name)
    return problems


def check_expired(exceptions, now):
    problems = []
    for exception in exceptions:
        expires_at = datetime.strptime(exception["expires"], TIME_FORMAT)
        if expires_at <= now:
            problems.append(exception["id"])
    return problems


def check_dept(users, role_dept):
    problems = []
    for name, info in users.items():
        expected_dept = role_dept[info["role"]]
        if expected_dept != info["dept"]:
            problems.append(name)
    return problems


def run_checklist(state, now):
    users = state["users"]
    exceptions = state["exceptions"]
    role_dept = state["role_dept"]
    return [
        {"name": "퇴사자 계정 점검", "problems": check_employed(users)},
        {"name": "만료 예외 점검", "problems": check_expired(exceptions, now)},
        {"name": "부서와 역할 점검", "problems": check_dept(users, role_dept)},
    ]
