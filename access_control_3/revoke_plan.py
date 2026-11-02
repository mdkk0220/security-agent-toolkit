def exception_id(source):                                        # "예외 3번" 모양 문자열을 받는 함수
    """"예외 3번" 모양 문자열에서 예외 번호(3)를 꺼내 숫자로 리턴한다."""
    number_text = source.replace("예외 ", "")                      # "예외 3번" 에서 "예외 " 를 지워 "3번" 으로 만든다 (미리 채움)
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. number_text 에서 "번" 을 지운 문자열을 number_text 에 다시 담는다 (.replace("번", ""))
    # 2. number_text 를 숫자로 바꿔 리턴한다 (int)
    number_text = number_text.replace("번", "")                   # "번" 을 지워 "3" 으로 만든다
    return int(number_text)                                       # 문자열 "3" 을 숫자 3 으로 바꿔 리턴한다


def count_users_by_role(users):                                  # 사용자 딕셔너리를 받는 함수
    """역할마다 사용자가 몇 명인지 센 딕셔너리를 리턴한다(재직 여부와 상관없이 센다). 예: {"finance": 1, "sales": 2}"""
    counts = {}                                                  # 역할 → 사용자 수를 담을 빈 딕셔너리
    for info in users.values():                                  # 사용자 정보를 하나씩 꺼낸다(.values() 는 딕셔너리의 값만 꺼낸다)
        role = info["role"]                                      # 그 사용자의 역할
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. counts.get(role, 0) 을 old_count 에 담는다 (처음이면 0)
        # 4. counts[role] 를 old_count + 1 로 정한다
        old_count = counts.get(role, 0)                          # 그 역할의 지금까지 센 수(처음이면 0)
        counts[role] = old_count + 1                             # 1 늘려서 다시 적는다
    return counts                                                # 역할별 사용자 수를 리턴한다


def make_plan(finding, method, target, impact):                  # 회수 대상 · 방법 · 대상 · 영향 범위를 받는 함수
    """회수 대상을 복사해 method · target · impact 키를 추가한 계획 한 건을 리턴한다. impact 는 이 회수로 사라지는 (사용자, 권한)의 수다."""
    plan = finding.copy()                                        # 원래 권한은 바꾸지 않고 복사한다
    plan["method"] = method                                      # 회수 방법을 적는다
    plan["target"] = target                                      # 실제로 지울 대상(예외 번호 · 사용자 · 역할)을 적는다
    plan["impact"] = impact                                      # 사라지는 (사용자, 권한)의 수를 적는다
    return plan                                                  # 계획 한 건을 리턴한다


def build_plan(finding, method, users, roles, role_counts):      # 회수 대상 한 건 · 회수 방법 · 사용자 · 역할 · 역할별 사용자 수를 받는 함수
    """회수 방법에 맞게 지울 대상(target)과 영향(impact)을 정해 계획 한 건을 리턴한다."""
    info = users[finding["user"]]                                # 그 사용자의 정보를 꺼낸다
    if method == "예외 삭제":                                    # 방법이 예외 삭제이면
        target = exception_id(finding["source"])                 # 지울 대상은 예외 번호
        return make_plan(finding, method, target, 1)             # 영향은 권한 1건
    if method == "역할 해제":                                    # 방법이 역할 해제이면
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. roles[info["role"]] 를 role_permissions 에 담는다 (그 사용자의 역할에 든 권한 리스트)
        # 6. len(role_permissions) 를 impact 에 담는다 (영향은 그 역할에 든 권한 수)
        role_permissions = roles[info["role"]]                   # 그 사용자의 역할에 든 권한 리스트
        impact = len(role_permissions)                           # 영향은 그 역할에 든 권한 수
        return make_plan(finding, method, finding["user"], impact)  # 지울 대상은 그 사용자의 이름 (미리 채움)
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. role_counts[info["role"]] 를 impact 에 담는다 (역할에서 권한 빼기: 영향은 그 역할을 가진 사용자 수)
    impact = role_counts[info["role"]]                           # 그 역할을 가진 사용자 수만큼 권한이 사라진다
    return make_plan(finding, method, info["role"], impact)      # 지울 대상은 역할 이름 (미리 채움)


def plan_revocation(findings, users, roles):                     # 회수 대상 리스트 · 사용자 딕셔너리 · 역할 딕셔너리를 받는 함수
    """회수 대상마다 회수 방법을 정해 계획 리스트를 리턴한다. 실제로는 아무것도 지우지 않는다."""
    role_counts = count_users_by_role(users)                     # 역할마다 사용자가 몇 명인지 센다(반복 전에 한 번만)
    plans = []                                                   # 계획을 담을 빈 리스트
    for finding in findings:                                     # 회수 대상을 하나씩 꺼낸다
        info = users[finding["user"]]                            # 그 사용자의 정보를 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 8. finding["source"] 안에 "예외" 가 있으면 (in)
        # 9.   method 를 "예외 삭제" 로 정한다
        # 10. 그렇지 않고 info["employed"] 가 거짓이면 (elif not)
        # 11.  method 를 "역할 해제" 로 정한다
        # 12. 그렇지 않으면 (else)
        # 13.  method 를 "역할에서 권한 빼기" 로 정한다
        if "예외" in finding["source"]:                          # 예외로 받은 권한이면
            method = "예외 삭제"                                 # 그 예외를 지운다
        elif not info["employed"]:                               # 퇴사한 사용자의 역할 권한이면
            method = "역할 해제"                                 # 그 사용자의 역할을 해제한다
        else:                                                    # 재직 중인 사용자의 역할 권한이면
            method = "역할에서 권한 빼기"                        # 역할에서 그 권한을 뺀다
        plan = build_plan(finding, method, users, roles, role_counts)  # 계획 한 건을 만든다
        plans.append(plan)                                       # 방법에 맞는 계획을 만들어 계획 리스트에 추가한다
    return plans                                                 # 계획 리스트를 리턴한다
