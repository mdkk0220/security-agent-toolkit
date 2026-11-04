from rbac import USERS, check_permission
from role_admin import assign_role, revoke_access

CHECKS = [
    ("minsu", "SALES", "QUERY"),
    ("seoyeon", "SALES", "CHANGE"),
    ("seoyeon", "SETTLE", "QUERY"),
    ("junho", "SETTLE", "QUERY"),
]


def run_checks(title):
    print("---", title)
    for user, resource, action in CHECKS:
        ok, reason = check_permission(user, resource, action)
        print(user, resource, action, "->", ok, reason)


run_checks("인사 변경 전")
print("--- 인사팀 통보 처리")
print("입사 minsu", assign_role(USERS, "minsu", "sales"))
print("입사 hana", assign_role(USERS, "hana", "salse"))
print("hana 가 사용자에 들어갔나", "hana" in USERS)
print("이동 seoyeon", assign_role(USERS, "seoyeon", "finance"))
print("퇴사 junho", revoke_access(USERS, "junho"))
print("퇴사 ghost", revoke_access(USERS, "ghost"))
run_checks("인사 변경 후")
