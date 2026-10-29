import json                                                      # JSON 파일을 읽는 모듈을 불러온다
from pathlib import Path

with open(Path(__file__).with_name("roles.json"), encoding="utf-8") as f:  # 역할 파일을 연다
    ROLES = json.load(f)                                         # 역할 → 권한 목록 딕셔너리로 읽는다
with open(Path(__file__).with_name("users.json"), encoding="utf-8") as f:  # 사용자 파일을 연다
    USERS = json.load(f)                                         # 사용자 → 정보 딕셔너리로 읽는다


def check_permission(user, resource, action):                    # 사용자 · 자원 · 행위를 받는 함수
    """(허용 여부, 이유)를 리턴한다. 허용 목록에 없으면 모두 거부한다."""   # 함수 첫 줄의 """ … """ 는 함수 설명 글이고 실행에는 영향이 없다
    if user not in USERS:                                        # 사용자 파일에 없는 계정이면
        return False, "등록되지 않은 사용자"                       # 바로 거부하고 함수를 끝낸다
    if not USERS[user]["employed"]:                              # 재직 중이 아니면
        return False, "퇴사한 계정"                                # 거부하고 함수를 끝낸다
    role = USERS[user]["role"]                                   # 이 사용자의 역할을 꺼낸다
    if role not in ROLES:                                        # 역할 파일에 없는 역할이면
        return False, "역할이 없음"                                # 거부하고 함수를 끝낸다
    permission = f"{resource}:{action}"                          # "자원:행위" 모양 글자로 합친다
    if permission not in ROLES[role]:                            # 그 역할의 권한 목록에 없으면
        return False, "권한 없음"                                  # 거부하고 함수를 끝낸다

    return True, "허용"                                          # 모든 검사를 지나면 허용한다
