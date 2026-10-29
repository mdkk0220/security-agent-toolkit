from rbac import USERS, ROLES                                    # 10/21(수)에 만든 사용자 · 역할 딕셔너리를 불러온다
from exception_policy import EXCEPTIONS                          # 10/22(목)에 만든 예외 목록을 불러온다


def role_entries(user, info):                                    # 사용자 이름과 그 사용자의 정보 딕셔너리를 받는 함수
    """사용자 한 명이 역할로 받은 권한을 현황의 권한 한 건씩 만들어 목록으로 리턴한다."""
    role = info["role"]                                          # 그 사용자의 역할을 꺼낸다
    entries = []                                                 # 역할로 받은 권한을 담을 빈 목록
    for permission in ROLES.get(role, []):                       # 역할의 권한을 하나씩 꺼낸다(역할 파일에 없는 역할이면 빈 목록)
        entry = {"user": user, "permission": permission, "source": f"역할 {role}", "employed": info["employed"]}  # 현황의 권한 한 건을 만든다
        entries.append(entry)                                    # 목록에 추가한다
    return entries                                               # 역할로 받은 권한 목록을 리턴한다


def build_access_list():                                         # 지금 부여돼 있는 권한을 모두 모아 목록으로 만드는 함수
    """부여돼 있는 권한을 모아 리턴한다. 목록의 한 건 = 사용자 한 명의 권한 하나(역할로 받았거나 예외로 받은 것)."""
    access_list = []                                             # 현황을 담을 빈 목록
    for user, info in USERS.items():                             # 사용자를 한 명씩 꺼낸다
        access_list = access_list + role_entries(user, info)     # 그 사용자가 역할로 받은 권한 목록을 현황 뒤에 이어 붙인다
    for exception in EXCEPTIONS:                                 # 예외를 하나씩 꺼낸다
        user = exception["user"]                                 # 예외를 받은 사용자 이름을 꺼낸다
        entry = {"user": user, "permission": exception["permission"], "source": f"예외 {exception['id']}번", "employed": USERS[user]["employed"]}  # 현황의 권한 한 건을 만든다
        entry["expires"] = exception["expires"]                  # 예외에만 있는 만료 시각 키를 추가한다
        access_list.append(entry)                                # 현황에 추가한다
    return access_list                                           # 현황을 리턴한다
