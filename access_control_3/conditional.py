from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다
from policy import evaluate_access                               # 10/22(목)에 만든 기본 판정 함수를 불러온다


def load_rules(path):                                            # 조건 파일 경로를 받는 함수
    """조건 파일을 읽어 조건 딕셔너리의 리스트를 리턴한다. 파일이 없거나 깨졌으면 빈 리스트를 리턴한다."""
    return load_json(path, [])                                   # 안전하게 읽는다(못 읽으면 두 번째 값인 빈 리스트를 리턴한다)


def is_work_time(rule, now):                                     # 조건 한 건과 요청 시각(datetime)을 받는 함수
    """요청 시각의 시가 조건의 허용 시간대 안이면 True, 밖이면 False 를 리턴한다. 끝 시각은 포함하지 않는다."""
    start, end = rule["hours"]
    hour = now.hour
    return start <= hour < end


def is_allowed_network(rule, network):                           # 조건 한 건과 접속 위치를 받는 함수
    """접속 위치가 조건의 허용 접속 위치에 들어 있으면 True, 아니면 False 를 리턴한다."""
    allowed_networks = rule["networks"]
    return network in allowed_networks


def evaluate_conditional(user, resource, action, network, now, rules):   # 사용자 · 자원 · 행위 · 접속 위치 · 요청 시각(datetime) · 조건 리스트를 받는 함수
    """(허용 여부, 이유)를 리턴한다. 기본 판정이 허용이어도 그 권한의 조건(업무 시간 · 접속 위치)에 어긋나면 거부한다."""
    ok, reason = evaluate_access(user, resource, action, now)    # 먼저 10/22(목)의 기본 판정을 한다 (미리 채움)
    if not ok:                                                   # 기본 판정이 거부이면
        return False, reason                                     # 그 이유로 바로 거부한다
    permission = f"{resource}:{action}"                          # "자원:행위" 모양 문자열로 합친다
    for rule in rules:                                           # 조건을 하나씩 꺼낸다
        if rule["permission"] == permission:                     # 이 권한에 걸린 조건이면
            if not is_work_time(rule, now):
                return False, "업무 시간 밖"
            if not is_allowed_network(rule, network):
                return False, "허용되지 않은 접속 위치"
    return True, reason                                          # 어긋나는 조건이 없으면 기본 판정의 이유로 허용한다
