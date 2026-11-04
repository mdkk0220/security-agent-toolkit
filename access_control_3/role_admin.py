from rbac import ROLES


def assign_role(users, name, role):
    """Assign a valid role to a new or existing user."""
    if role not in ROLES:
        return False, "없는 역할"
    users[name] = {"role": role, "employed": True}
    return True, "부여"


def revoke_access(users, name):
    """Mark an existing user as no longer employed."""
    if name not in users:
        return False, "없는 사용자"
    users[name]["employed"] = False
    return True, "회수"
