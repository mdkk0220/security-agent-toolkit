import json                                                      # JSON 파일을 읽는 모듈을 불러온다


def load_json(path, default):                                    # 파일 경로와 실패했을 때 쓸 기본값을 받는 함수
    """JSON 파일을 읽어 리턴한다. 파일이 없거나 깨졌으면 경고를 출력하고 default 를 리턴한다."""
    try:                                                         # 아래를 시도한다
        with open(path, encoding="utf-8") as f:                  # 파일을 연다
            return json.load(f)                                  # 읽은 내용을 바로 리턴한다
    except FileNotFoundError:                                    # 파일이 없으면
        print("[경고] 설정 파일 없음:", path)                      # 경고를 남기고
        return default                                           # 기본값을 리턴한다
    except json.JSONDecodeError:                                 # JSON 이 깨졌으면
        print("[경고] 설정 파일 깨짐:", path)                      # 경고를 남기고
        return default                                           # 기본값을 리턴한다
