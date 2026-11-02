import json                                                      # JSON 파일을 쓰는 모듈을 불러온다


def remove_exception(exceptions, target_id):                     # 예외 리스트와 지울 예외 번호를 받는 함수
    """예외 리스트에서 번호가 target_id 인 예외 한 건을 지운다. 지웠으면 True, 못 찾았으면 False 를 리턴한다."""
    for exc in exceptions:                                       # 예외를 하나씩 꺼낸다
        if exc["id"] == target_id:                               # 번호가 같으면
            exceptions.remove(exc)                               # 리스트에서 그 예외를 지운다
            return True                                          # 지웠다고 알리고 함수를 끝낸다
    return False                                                 # 끝까지 못 찾았으면 False 를 리턴한다


def apply_plan(plan, users, roles, exceptions):                  # 계획 한 건 · 사용자 · 역할 · 예외 리스트를 받는 함수
    """계획 한 건의 회수 방법대로 프로그램 안의 데이터를 실제로 바꾼다. 승인 상태는 보지 않는다(승인 확인은 호출하는 쪽이 한다)."""
    if plan["method"] == "예외 삭제":                            # 방법이 예외 삭제이면
        remove_exception(exceptions, plan["target"])             # 예외 리스트에서 그 번호의 예외를 지운다
    elif plan["method"] == "역할 해제":                          # 방법이 역할 해제이면
        user_info = users[plan["target"]]                        # 그 사용자의 정보 딕셔너리를 꺼낸다
        user_info["role"] = ""                                   # 역할을 빈 문자열로 바꾼다(어떤 역할의 권한도 받지 않게 된다)
    else:                                                        # 방법이 역할에서 권한 빼기이면
        role_permissions = roles[plan["target"]]                 # 그 역할의 권한 리스트를 꺼낸다
        role_permissions.remove(plan["permission"])              # 그 리스트에서 그 권한을 지운다


def save_log(log, path):                                         # 이력 리스트와 저장할 파일 경로를 받는 함수
    """이력 리스트를 JSON 파일로 저장하고 저장한 건수를 리턴한다. 한글이 그대로 보이게 쓴다."""
    with open(path, "w", encoding="utf-8") as f:                 # 파일을 쓰기 모드("w")로 연다
        json.dump(log, f, ensure_ascii=False, indent=2)          # 이력을 파일에 JSON 으로 쓴다
    return len(log)                                              # 저장한 건수를 리턴한다


def execute_revocation(plans, users, roles, exceptions, now):    # 계획 · 사용자 · 역할 · 예외 리스트 · 지금 시각 문자열을 받는 함수
    """승인 불필요이거나 승인됨인 계획만 실제로 실행하고, 이력 리스트를 리턴한다. 승인 대기인 계획은 실행하지 않고 이력에 「대기」로 남긴다."""
    log = []                                                     # 이력을 담을 빈 리스트
    for plan in plans:                                           # 계획을 하나씩 꺼낸다
        if plan["approval"] == "승인 대기":                      # 아직 승인을 기다리는 계획이면
            result = "대기"                                      # 실행하지 않고 대기로 남긴다
        else:                                                    # 승인 불필요이거나 승인된 계획이면
            apply_plan(plan, users, roles, exceptions)           # 실제로 회수한다
            result = "실행"                                      # 실행했다고 적는다
        entry = {
            "time": now,                                         # 시각
            "user": plan["user"],                                # 사용자
            "permission": plan["permission"],                    # 권한
            "method": plan["method"],                            # 회수 방법
            "approval": plan["approval"],                        # 승인 상태
            "result": result,                                    # 결과(실행 또는 대기)
        }
        log.append(entry)                                        # 이력 한 건을 만들어 이력 리스트에 추가한다
    return log                                                   # 이력 리스트를 리턴한다
