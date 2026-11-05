import json

with open("config/roles.json", encoding="utf-8") as roles_file:
    ROLES = json.load(roles_file)
with open("config/users.json", encoding="utf-8") as users_file:
    USERS = json.load(users_file)


def check_permission(user, resource, action):
    """Return whether a request is allowed and the reason for the decision."""
    if user not in USERS:
        return False, "등록되지 않은 사용자"
    if not USERS[user]["employed"]:
        return False, "퇴사한 계정"
    role = USERS[user]["role"]
    if role not in ROLES:
        return False, "역할이 없음"
    permission = f"{resource}:{action}"
    if permission not in ROLES[role]:
        return False, "권한 없음"
    return True, "허용"
