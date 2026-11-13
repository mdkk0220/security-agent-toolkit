# 11/13(금) 오전 · 5과목 자동 대응(SOAR) ⑧ — 초동 대응 리포트(incident report) 작성 · 승인 게이트(approval gate)와 위험 점수 기반 승인 정책 · 오탐(false positive) 롤백(rollback)과 복구 검증

<mark style="background:#e0d4ff">어제까지 조치 · 티켓 · 알림 · 에스컬레이션</mark>(escalation, 에스컬레이션: 정해진 시간 안에 처리되지 않은 사건을 상위 담당자에게 넘겨 처리하게 하는 일)을 구현했습니다. 오늘 오전에는 <mark>**처리 결과를 리포트로 보고하고, 자동 실행해도 되는 조치와 사람의 승인이 필요한 조치를 구분하고, 오탐으로 판명된 조치를 원래 상태로 복원하는 부분**</mark>을 구현합니다.

- **2교시**: 어제 근무의 티켓을 판다스(pandas, 판다스: 표 모양 데이터를 다루는 파이썬 도구) 표로 바꿔 집계(aggregation, 어그리게이션: 값을 그룹별로 모아 개수 · 평균을 구하는 일)하고, 조치 기록과 대조(reconciliation, 레컨실리에이션: 두 기록이 서로 맞는지 맞춰 보는 일)해 초동 대응 리포트(incident report, 인시던트 리포트: 사건의 현황과 처리 내용을 정리해 전달하는 문서) 파일을 작성합니다(`report.py`).
- **3교시**: 조치 요청마다 위험 점수(risk score, 리스크 스코어: 조치의 위험을 점수로 환산한 값)를 합산해 「자동 · 승인 필요 · 차단 금지」로 분류하는 승인 게이트를 구현합니다. <mark style="background:#ffdcb0">승인 기준은 설정 파일로 분리합니다</mark>(`approval_gate.py`).
- **4교시**: 오탐(false positive, 폴스 포지티브: 위협이 아닌 활동을 위협으로 잘못 판정한 알림) 신고를 받으면 영향 확인(impact assessment: 조치가 실제로 바꾼 대상을 파악하는 일)을 하고, <mark style="background:#e0d4ff">수요일의 되돌리기 함수</mark>로 롤백(rollback, 롤백: 조치 이전 상태로 복원하는 일)한 뒤, 복구 확인(recovery verification: 실제 상태가 복원됐는지 다시 점검하는 일)까지 처리합니다(`false_positive.py`).

깃허브에 올리는 일은 오후 6교시 마지막에 합니다. 새 문법은 2교시의 판다스 세 가지(열(column, 컬럼: 표의 세로 줄)끼리 빼기 · 그룹마다 평균 `mean` · 반올림 `round`)입니다. 보고서의 🔍 질문은 <mark>내 출력 값을 근거로 이유까지</mark> 씁니다. 들여쓰기(줄 앞의 빈칸)는 각 번호 주석과 같은 위치에서 시작합니다. 각 번호 주석 바로 아래에 한 줄을 씁니다. 주석은 지우지 않습니다.

📎 **이전 파일**: <mark style="background:#e0d4ff">월요일의 `incident.py`</mark>(`load_json` · `save_json`)를 모든 교시에서 씁니다. 4교시는 <mark style="background:#e0d4ff">수요일의 `rollback.py`</mark> 와, 그 파일이 직접 또는 다른 파일을 거쳐 가져와 사용(import)하는 `undo_actions.py` · `account_actions.py` · `ip_actions.py` · `containment_store.py` 도 씁니다. 없는 파일은 아래 시작하기의 「🛟 이전 파일이 없을 때」 코드 상자로 만듭니다.

🔤 **줄임말 이름 안내**: 이 문서의 코드와 파일에는 줄임말로 된 이름이 있습니다. 처음 보면 뜻을 알기 어려워서 아래에 풀어 둡니다. 이미 배포한 파일과 맞추기 위해 이름은 그대로 쓰고 뜻만 설명합니다.
  - `ack` · `acked` 는 acknowledge(확인하다) · acknowledged(확인했다)의 줄임말입니다. 담당자가 티켓을 처음 확인했다는 뜻입니다.
  - `acked_at` 은 처음 확인한 시각(분), `ack_minutes` 는 확인까지 걸린 분, `acked` 는 확인한 티켓만 남긴 표, `mean_ack_by_grade` 는 등급마다 확인까지 걸린 분의 평균을 구하는 함수입니다.
  - `sla` 는 서비스 수준 협약(SLA, Service Level Agreement)의 줄임말입니다. 이 문서에서는 응답 기한을 뜻합니다.
  - `sla_due` 는 응답해야 하는 시각입니다.

## 시작하기

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** 5과목 폴더로 들어가 파일을 확인합니다. <mark>`ls` 결과에 `incident.py` 와 `rollback.py` 가 보이면</mark> 됩니다. 4교시에는 수요일의 `undo_actions.py` · `account_actions.py` · `ip_actions.py` · `containment_store.py` 도 필요합니다(없으면 위 📎 의 절에서 복사).
   ```bash
   pwd
   cd soar_response
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `cd 폴더이름` 그 폴더로 이동 · `ls` 폴더 안의 파일 이름 보기
   - `pwd` 가 이미 `…/soar_response` 로 끝나면 `cd soar_response` 는 건너뜁니다.
3. 오늘 받은 파일 두 개(`day05_am_report_gate.md`, `day05_am_report.md`)를 `soar_response` 폴더로 옮기고, 보고서 제목의 `이름` 을 내 이름으로 바꿉니다.
4. **[터미널]** 판다스를 불러올 수 있는지 확인합니다(맥북은 `python3`). <mark>`판다스 불러오기 성공` 이 나와야</mark> 합니다.
   ```bash
   python -c "import pandas; print('판다스 불러오기 성공')"
   ```
   - `No module named 'pandas'`(판다스가 설치되어 있지 않다는 뜻)가 나오면 터미널(가상환경이 켜진 상태)에서 `pip install pandas`(판다스를 설치하는 명령)를 입력한 뒤 다시 확인합니다.
5. **[터미널]** 2교시 데이터 파일 두 개를 만들고 **[VS Code]** 에서 열어 아래 내용을 붙여 넣습니다.
   ```bash
   touch day05_tickets.json day05_actions.json
   ls
   ```

**`day05_tickets.json`** — 어제(11/12(목)) 근무 3시간이 끝났을 때의 티켓 7장입니다.

- **무엇인가**:
  - 어제 6교시가 저장한 `shift_tickets.json` 에서 리포트에 쓰는 키만 남긴 것입니다.
  - `incidents` 는 티켓 하나로 병합(merge)된 인시던트(incident, 인시던트: 탐지된 보안 사건 하나)의 번호 리스트입니다.
  - `created_at`(티켓 생성 시각) · `sla_due`(응답 기한 시각, 담당자가 이 시각까지 확인해야 하는 마감 시각. SLA 는 Service Level Agreement, 에스엘에이: 담당자가 응답해야 하는 시간을 미리 약속한 서비스 수준 협약입니다) · `acked_at`(확인 시각, acknowledge: 담당자가 사건을 처음 확인한 시각) · `resolved_at`(해결 시각)은 모두 근무를 시작한 때를 0분으로 놓고, 그때부터 몇 분이 지났는지를 적은 숫자입니다. <mark style="background:#ffdcb0">아직 확인하지 않았거나 해결하지 않았으면 `-1` 입니다.</mark>
- **어디에 쓰나**: 2교시 리포트의 재료입니다.

```
[
  {"id": "TCK-1", "incidents": ["INC-201", "INC-205", "INC-209"], "entity": "dami", "rule": "퇴사한 계정", "grade": "high", "status": "해결", "created_at": 0, "sla_due": 15, "acked_at": 10, "resolved_at": 45},
  {"id": "TCK-2", "incidents": ["INC-202", "INC-206"], "entity": "198.51.100.90", "rule": "경로 스캔", "grade": "low", "status": "열림", "created_at": 3, "sla_due": 243, "acked_at": -1, "resolved_at": -1},
  {"id": "TCK-3", "incidents": ["INC-203"], "entity": "gaeun", "rule": "규칙은 허용인데 서버가 거절", "grade": "mid", "status": "해결", "created_at": 8, "sla_due": 68, "acked_at": 80, "resolved_at": 120},
  {"id": "TCK-4", "incidents": ["INC-204"], "entity": "seoyeon", "rule": "대량 다운로드", "grade": "mid", "status": "확인 중", "created_at": 12, "sla_due": 72, "acked_at": 140, "resolved_at": -1},
  {"id": "TCK-5", "incidents": ["INC-207"], "entity": "203.0.113.250", "rule": "경로 스캔", "grade": "low", "status": "열림", "created_at": 30, "sla_due": 270, "acked_at": -1, "resolved_at": -1},
  {"id": "TCK-6", "incidents": ["INC-208"], "entity": "hana", "rule": "업무 시간 밖 로그인", "grade": "mid", "status": "해결", "created_at": 35, "sla_due": 95, "acked_at": 90, "resolved_at": 130},
  {"id": "TCK-7", "incidents": ["INC-210", "INC-211"], "entity": "dami", "rule": "퇴사한 계정", "grade": "high", "status": "확인 중", "created_at": 95, "sla_due": 110, "acked_at": 105, "resolved_at": -1}
]
```

**`day05_actions.json`** — 어제 자동 대응이 남긴 조치 기록 9건에, 설명을 위해 만든 `INC-212` 1건을 더한 10건입니다.

- **무엇인가**:
  - <mark style="background:#e0d4ff">수요일에 만든 조치 기록</mark>(감사 기록, audit log: 조치를 순서대로 남긴 기록)에서 `reason` 키만 뺀 꼴입니다. `before` 는 조치 전 상태, `after` 는 조치 후 상태입니다.
  - `INC-212` 는 근무가 끝나기 직전에 `yuna` 계정을 잠근 기록입니다. 티켓 생성 단계가 실패해서 이 인시던트에는 티켓이 없습니다.
- **어디에 쓰나**: 2교시 리포트는 티켓과 조치 기록을 대조해 티켓마다 조치 기록 수를 세고, 티켓이 없는 조치(추적 누락)를 찾습니다.

```
[
  {"incident": "INC-201", "action": "계정 잠금", "target": "dami", "before": "잠기지 않음", "after": "잠김"},
  {"incident": "INC-201", "action": "세션 종료", "target": "dami", "before": "세션 2개", "after": "세션 0개"},
  {"incident": "INC-202", "action": "IP 차단", "target": "198.51.100.90", "before": "차단되지 않음", "after": "차단됨"},
  {"incident": "INC-205", "action": "계정 잠금", "target": "dami", "before": "잠김", "after": "잠김"},
  {"incident": "INC-206", "action": "IP 차단", "target": "198.51.100.90", "before": "차단됨", "after": "차단됨"},
  {"incident": "INC-207", "action": "IP 차단", "target": "203.0.113.250", "before": "차단되지 않음", "after": "차단되지 않음 (확인 실패)"},
  {"incident": "INC-209", "action": "계정 잠금", "target": "dami", "before": "잠김", "after": "잠김"},
  {"incident": "INC-210", "action": "계정 잠금", "target": "dami", "before": "잠김", "after": "잠김"},
  {"incident": "INC-211", "action": "계정 잠금", "target": "dami", "before": "잠김", "after": "잠김"},
  {"incident": "INC-212", "action": "계정 잠금", "target": "yuna", "before": "잠기지 않음", "after": "잠김"}
]
```

6. **[터미널]** 파일이 정상인지 확인합니다(맥북은 `python3`). <mark>`7 10` 이 나와야</mark> 합니다.
   ```bash
   python -c "import json; print(len(json.load(open('day05_tickets.json', encoding='utf-8'))), len(json.load(open('day05_actions.json', encoding='utf-8'))))"
   ```

### 🛟 이전 파일이 없을 때 (월요일 · 수요일 파일)

월요일이나 수요일에 결석했거나 파일을 지운 경우에만 만듭니다. **이미 있는 파일은 건너뜁니다.** 먼저 **[터미널]** 에서 빈 파일을 만듭니다. 이미 있는 파일은 `touch` 가 그대로 둡니다.

```bash
touch incident.py containment_store.py account_actions.py ip_actions.py undo_actions.py rollback.py
ls
```

- 명령 풀이: `touch 파일이름들` 빈 파일 만들기 · `ls` 폴더 안의 파일 이름 보기
- 아래 코드 상자 여섯 개를 **[VS Code]** 에서 같은 이름의 파일에 순서대로 붙여 넣고 저장합니다. 이미 있는 파일은 붙여 넣지 않습니다. 오전 2 · 3교시는 `incident.py` 만 있으면 되고, 나머지 다섯 개는 4교시에서 씁니다.

**`incident.py`** — 월요일 파일에서 오늘 쓰는 두 함수(`load_json` · `save_json`)만 담았습니다. 월요일 파일 전체가 있으면 그것을 그대로 씁니다.

```python
import json                                                  # JSON 파일을 읽고 쓰기 위해 json 을 불러온다


def load_json(path):                                         # 파일 경로를 받는 함수
    """JSON 파일을 읽어 리스트나 딕셔너리로 리턴한다.
    인시던트와 플레이북 등록 파일을 읽을 때 쓴다.
    """
    with open(path, encoding="utf-8") as file:               # 파일을 읽기 모드로 연다
        data = json.load(file)                               # JSON 글자를 파이썬 값으로 바꾼다
    return data                                              # 읽은 값을 리턴한다


def save_json(data, path):                                   # 저장할 값과 파일 경로를 받는 함수
    """값을 JSON 파일로 저장한다.
    실행 결과 상태와 감사 기록을 남길 때 쓴다.
    """
    with open(path, "w", encoding="utf-8") as file:          # 파일을 쓰기 모드로 연다
        json.dump(data, file, ensure_ascii=False, indent=2)  # 한글은 그대로, 줄을 나눠 저장한다
```

**`containment_store.py`** — 수요일 오전 파일입니다. 조치 기록 한 건을 만들고 조치 상태를 파일로 저장 · 읽기 합니다.

```python
import copy                                                           # 처음 상태를 복사해 쓰기 위해 copy 를 불러온다
from incident import load_json, save_json                             # 어제 파일의 파일 읽기 · 쓰기 함수를 불러온다

STATE_PATH = "containment_state.json"                                 # 연습용 시스템 상태를 저장할 파일 이름
LOG_PATH = "containment_log.json"                                     # 조치 기록을 저장할 파일 이름
INITIAL_STATE = {                                                     # 수업을 시작할 때의 연습용 시스템 상태
    "locked_users": ["junho"],                                        # 이미 잠겨 있는 계정 : junho 는 수업 전부터 잠겨 있다
    "blocked_ips": [],                                                # 차단한 IP 리스트 : 처음에는 비어 있다
    "block_expiry": {},                                               # IP 별 차단이 끝나는 시각(분) : 처음에는 비어 있다
    "clock": 0,                                                       # 연습용 시스템의 시계(분) : 0 에서 시작한다
    "sessions": {"dami": ["S-101", "S-102"], "seoyeon": ["S-201"], "gaeun": ["S-301"], "jiwoo": ["S-401"], "junho": ["S-501"], "hana": ["S-601"]},  # 계정별로 열려 있는 로그인 세션
}


def new_state():                                                      # 인자가 없는 함수
    """처음 상태를 복사해 새 연습용 시스템 상태를 리턴한다.
    실행할 때마다 같은 상태에서 시작해 결과를 비교할 때 쓴다.
    """
    return copy.deepcopy(INITIAL_STATE)                               # 처음 상태의 복사본을 리턴한다


def save_state(state):                                                # 연습용 시스템 상태를 받는 함수
    """상태를 파일에 저장한다.
    다음 프로그램이 이어서 읽을 수 있게 할 때 쓴다.
    """
    save_json(state, STATE_PATH)                                      # 상태를 JSON 파일로 저장한다


def load_state():                                                     # 인자가 없는 함수
    """저장해 둔 상태 파일을 읽어 리턴한다.
    저장이 제대로 됐는지 확인하거나 이어서 일할 때 쓴다.
    """
    return load_json(STATE_PATH)                                      # 상태 파일을 읽어 리턴한다


def reset_log():                                                      # 인자가 없는 함수
    """조치 기록 파일을 빈 리스트로 비운다.
    실행할 때마다 기록을 처음부터 쌓을 때 쓴다.
    """
    save_json([], LOG_PATH)                                           # 빈 리스트를 기록 파일로 저장한다


def make_record(action, target, incident_id, before, after, reason):  # 조치 이름 · 대상 · 인시던트 번호 · 조치 전 · 조치 후 · 이유를 받는 함수
    """조치 한 건(무엇을 · 누구에게 · 조치 전 · 조치 후 · 이유)의 기록을 딕셔너리로 만들어 리턴한다.
    조치 전과 후 상태를 함께 남겨 두고 싶을 때 쓴다.
    """
    record = {"action": action, "target": target, "incident": incident_id, "before": before, "after": after, "reason": reason}  # 조치 한 건의 기록을 딕셔너리로 만든다
    return record                                                     # 기록 한 건을 리턴한다


def append_log(record):                                               # 기록 한 건을 받는 함수
    """기록 파일을 읽어 기록 한 건을 더하고 다시 저장한다. 파일이 아직 없으면 빈 리스트로 시작한다.
    조치할 때마다 기록을 한 건씩 쌓아 둘 때 쓴다.
    """
    try:                                                              # 파일 읽기를 시도한다 — 미리 채운 줄
        log = load_json(LOG_PATH)                                     # 기록 파일을 읽는다 — 미리 채운 줄
    except FileNotFoundError:                                         # 파일이 없으면 — 미리 채운 줄
        log = []                                                      # 빈 리스트로 시작한다 — 미리 채운 줄
    log.append(record)                                                # 기록 한 건을 리스트에 추가한다
    save_json(log, LOG_PATH)                                          # 기록 파일로 다시 저장한다
```

**`account_actions.py`** — 수요일 오전 파일입니다. 계정을 잠그고 해제합니다.

```python
from containment_store import make_record                                             # 기록 한 건을 만드는 함수를 불러온다


def check_policy(user, vip_accounts):                                                 # 계정 이름과 VIP 계정 리스트를 받는 함수
    """자동으로 조치하면 안 되는 계정(VIP)이면 그 이유 문장을, 아니면 빈 글자("")를 리턴한다.
    경로에서 이미 걸렀어도 조치 함수가 마지막으로 한 번 더 막고 싶을 때 쓴다.
    """
    if user in vip_accounts:                                                          # VIP 계정이면
        return "VIP 계정이라 자동 조치 대상이 아님"                                   # 막는 이유를 리턴한다
    return ""                                                                         # 막을 이유가 없으면 빈 글자를 리턴한다 — 미리 채운 줄


def verify_locked(user, state):                                                       # 계정 이름과 연습용 시스템 상태를 받는 함수
    """계정이 잠긴 계정 리스트에 들어 있으면 True, 없으면 False 를 리턴한다.
    잠그라고 호출한 것과 실제로 잠긴 것이 같은지 조치 뒤에 확인할 때 쓴다.
    """
    return user in state["locked_users"]                                              # 잠긴 계정 리스트 안에 있는지 확인한 결과를 리턴한다


def lock_account(user, state, vip_accounts, incident_id, reason):                     # 계정 · 상태 · VIP 리스트 · 인시던트 번호 · 이유를 받는 함수
    """VIP 인지 먼저 확인하고 계정을 잠근 뒤, 실제로 잠겼는지 다시 확인해 조치 기록 한 건을 리턴한다.
    VIP 이거나 이미 잠겨 있으면 잠그지 않고 그 이유를 기록에 남긴다.
    """
    blocked = check_policy(user, vip_accounts)                                        # 자동 조치를 막을 이유를 구한다 — 미리 채운 줄
    if blocked != "":                                                                 # 막을 이유가 있으면 — 미리 채운 줄
        return make_record("계정 잠금", user, incident_id, "변경 없음", "변경 없음", blocked)  # 바꾸지 않고 이유를 기록한다 — 미리 채운 줄
    if user in state["locked_users"]:                                                 # 이미 잠겨 있으면 — 미리 채운 줄
        return make_record("계정 잠금", user, incident_id, "잠김", "잠김", "이미 잠겨 있어 변경 없음")  # 바꾸지 않고 기록한다 — 미리 채운 줄
    state["locked_users"].append(user)                                                # 잠긴 계정 리스트에 추가한다
    after = "잠김"                                                                    # 조치 뒤 상태 : 일단 잠겼다고 적고 — 미리 채운 줄
    if not verify_locked(user, state):                                                # 실제로 확인해 잠기지 않았으면 — 미리 채운 줄
        after = "잠기지 않음 (확인 실패)"                                             # 확인 실패라고 고쳐 적는다 — 미리 채운 줄
    return make_record("계정 잠금", user, incident_id, "잠기지 않음", after, reason)  # 조치 전 · 후 상태와 함께 기록한다 — 미리 채운 줄


def unlock_account(user, state, incident_id, reason):                                 # 계정 · 상태 · 인시던트 번호 · 이유를 받는 함수
    """잠긴 계정을 해제하고 실제로 해제됐는지 확인해 조치 기록 한 건을 리턴한다.
    오탐으로 확인된 계정을 되돌릴 때 쓴다.
    """
    if user not in state["locked_users"]:                                             # 잠겨 있지 않으면 — 미리 채운 줄
        return make_record("계정 해제", user, incident_id, "잠기지 않음", "잠기지 않음", "잠겨 있지 않아 변경 없음")  # 바꾸지 않고 기록한다 — 미리 채운 줄
    state["locked_users"].remove(user)                                                # 잠긴 계정 리스트에서 제거한다
    after = "잠기지 않음"                                                             # 조치 뒤 상태 : 일단 해제됐다고 적고 — 미리 채운 줄
    if verify_locked(user, state):                                                    # 실제로 확인해 아직 잠겨 있으면 — 미리 채운 줄
        after = "잠김 (확인 실패)"                                                    # 확인 실패라고 고쳐 적는다 — 미리 채운 줄
    return make_record("계정 해제", user, incident_id, "잠김", after, reason)         # 조치 전 · 후 상태와 함께 기록한다 — 미리 채운 줄
```

**`ip_actions.py`** — 수요일 오전 파일입니다. IP 를 차단하고 해제합니다.

```python
from containment_store import make_record                                                     # 기록 한 건을 만드는 함수를 불러온다

SHARED_IP_LIMIT = 2                                                                           # 한 IP 를 쓰는 계정이 이 수 이상이면 공유 IP 로 본다
DEFAULT_TTL = 120                                                                             # 차단을 유지하는 시간(분)


def is_in_allowlist(ip, allowlist_ips):                                                       # IP 와 허용 목록을 받는 함수
    """IP 가 허용 목록에 있으면 True, 없으면 False 를 리턴한다.
    협력사 사무실처럼 차단하면 안 되는 IP 를 걸러낼 때 쓴다.
    """
    return ip in allowlist_ips                                                                # 허용 목록 안에 있는지 확인한 결과를 리턴한다


def count_users_on_ip(ip, ip_users):                                                          # IP 와 IP 별 사용 계정 딕셔너리를 받는 함수
    """그 IP 를 쓰는 계정이 몇 개인지 리턴한다. ip_users.json 에 없는 IP 는 0 을 리턴한다.
    차단하면 정상 사용자가 몇 명 영향을 받는지 확인할 때 쓴다.
    """
    return len(ip_users.get(ip, []))                                                          # 그 IP 를 쓰는 계정 수를 리턴한다 (목록에 없으면 0)


def check_ip_policy(ip, allowlist_ips, ip_users):                                             # IP · 허용 목록 · 사용 계정 딕셔너리를 받는 함수
    """자동으로 차단하면 안 되는 IP 이면 그 이유 문장을, 아니면 빈 글자("")를 리턴한다.
    허용 목록 IP 이거나 여러 계정이 함께 쓰는 IP 를 차단하기 전에 가려낼 때 쓴다.
    """
    if is_in_allowlist(ip, allowlist_ips):                                                    # 허용 목록 IP 이면 — 미리 채운 줄
        return "허용 목록 IP 라서 차단하지 않음"                                              # 이유를 리턴한다 — 미리 채운 줄
    if count_users_on_ip(ip, ip_users) >= SHARED_IP_LIMIT:                                    # 여러 계정이 함께 쓰는 IP 이면 — 미리 채운 줄
        return "여러 계정이 함께 쓰는 IP 라서 담당자 승인 필요"                               # 이유를 리턴한다 — 미리 채운 줄
    return ""                                                                                 # 막을 이유가 없으면 빈 글자를 리턴한다 — 미리 채운 줄


def block_ip(ip, state, incident_id, reason, ttl):                                            # IP · 상태 · 인시던트 번호 · 이유 · 유지 시간을 받는 함수
    """IP 를 차단하고 끝나는 시각을 적은 뒤, 실제로 차단됐는지 확인해 기록 한 건을 리턴한다.
    영구 차단 대신, 시간이 지나면 자동으로 풀리는 임시 차단을 만들 때 쓴다.
    """
    state["blocked_ips"].append(ip)                                                           # 차단한 IP 리스트에 추가한다
    state["block_expiry"][ip] = state["clock"] + ttl                                          # 차단이 끝나는 시각을 적는다
    after = "차단됨"                                                                          # 조치 뒤 상태 : 일단 차단됐다고 적고 — 미리 채운 줄
    if ip not in state["blocked_ips"]:                                                        # 실제로 확인해 차단되지 않았으면 — 미리 채운 줄
        after = "차단되지 않음 (확인 실패)"                                                   # 확인 실패라고 고쳐 적는다 — 미리 채운 줄
    return make_record("IP 차단", ip, incident_id, "차단되지 않음", after, reason + " (" + str(ttl) + "분 뒤 자동 해제)")  # 조치 전 · 후 상태와 함께 기록한다 — 미리 채운 줄


def unblock_ip(ip, state, incident_id, reason):                                               # IP · 상태 · 인시던트 번호 · 이유를 받는 함수
    """차단한 IP 를 풀고 끝나는 시각 기록도 지운 뒤 기록 한 건을 리턴한다.
    시간이 끝나서 풀거나 오탐으로 풀 때 쓴다.
    """
    state["blocked_ips"].remove(ip)                                                           # 차단 리스트에서 제거한다 — 미리 채운 줄
    state["block_expiry"].pop(ip)                                                             # 끝나는 시각 기록도 지운다 — 미리 채운 줄
    return make_record("IP 해제", ip, incident_id, "차단됨", "차단되지 않음", reason)         # 조치 전 · 후 상태와 함께 기록한다 — 미리 채운 줄


def expire_blocks(state, incident_id):                                                        # 상태와 인시던트 번호를 받는 함수
    """끝나는 시각이 지난 차단을 모두 풀고 해제 기록 리스트를 리턴한다.
    임시 차단이 사람 손 없이 풀리게 할 때 쓴다.
    """
    records = []                                                                              # 해제 기록을 담을 빈 리스트
    for ip in list(state["blocked_ips"]):                                                     # 차단 리스트의 복사본에서 IP 를 하나씩 꺼낸다 (원본을 바꾸며 돌면 안 되기 때문이다)
        end_time = state["block_expiry"][ip]                                                  # 그 IP 의 차단이 끝나는 시각 — 미리 채운 줄
        if end_time <= state["clock"]:                                                        # 끝나는 시각이 지났으면
            records.append(unblock_ip(ip, state, incident_id, "차단 시간이 끝나 자동 해제"))  # 차단을 풀고 해제 기록을 모은다
    return records                                                                            # 해제 기록 리스트를 리턴한다
```

**`undo_actions.py`** — 수요일 오후 파일입니다. 조치 기록 한 건을 거꾸로 되돌립니다.

```python
from account_actions import unlock_account  # 오전 2교시에 만든 계정 해제 함수를 불러온다
from ip_actions import unblock_ip           # 오전 3교시에 만든 IP 해제 함수를 불러온다


def undo_account(record, state):            # 되돌릴 조치 기록과 연습용 시스템 상태를 받는 함수
    """계정 잠금 기록 한 건을 되돌려 계정을 해제하고, 해제 기록을 리턴한다.
    자동으로 잠근 계정을 오탐이 확인된 뒤에 원래대로 풀 때 쓴다.
    """
    return unlock_account(record["target"], state, record["incident"], "되돌리기: " + record["reason"])  # 계정 해제를 실행하고 기록을 리턴한다


def undo_ip(record, state):                 # 되돌릴 조치 기록과 연습용 시스템 상태를 받는 함수
    """IP 차단 기록 한 건을 되돌려 IP 차단을 풀고, 해제 기록을 리턴한다.
    자동으로 차단한 IP 를 오탐이 확인된 뒤에 원래대로 풀 때 쓴다.
    """
    return unblock_ip(record["target"], state, record["incident"], "되돌리기: " + record["reason"])  # IP 해제를 실행하고 기록을 리턴한다


def undo_record(record, state):             # 되돌릴 조치 기록과 연습용 시스템 상태를 받는 함수
    """조치 종류(계정 잠금 · IP 차단)에 맞는 되돌리기 함수를 골라 불러서, 해제 기록을 리턴한다.
    기록 한 건을 받아 알맞은 방법으로 되돌릴 때 쓴다.
    """
    if record["action"] == "계정 잠금":     # 계정 잠금 기록이면 — 미리 채운 줄
        return undo_account(record, state)  # 계정을 해제한다 — 미리 채운 줄
    return undo_ip(record, state)           # 아니면 IP 차단 기록이므로 IP 를 해제한다 — 미리 채운 줄
```

**`rollback.py`** — 수요일 오후 파일입니다. 인시던트 한 건의 조치 기록을 찾아 되돌립니다.

```python
from containment_store import make_record                                    # 기록 한 건을 만드는 함수를 불러온다
from undo_actions import undo_record                                         # 방금 만든 되돌리기 함수를 불러온다

UNDOABLE_ACTIONS = ["계정 잠금", "IP 차단"]                                  # 해제로 되돌릴 수 있는 조치 이름


def find_incident_records(log, incident_id):                                 # 기록 리스트와 인시던트 번호를 받는 함수
    """기록 중 그 인시던트(알림 한 건)의 기록만 모은 뒤, 나중에 한 일이 먼저 오도록 순서를 뒤집어 리턴한다.
    조치를 거꾸로 되돌릴 때 쓴다.
    """
    found = []                                                               # 그 인시던트의 기록을 담을 빈 리스트
    for record in log:                                                       # 기록을 하나씩 꺼낸다
        action_name = record["action"]                                       # 기록의 조치 이름 — 미리 채운 줄
        if record["incident"] == incident_id:                                # 그 인시던트의 기록이면
            found.append(record)                                             # 모아 둔다
    return list(reversed(found))                                             # 순서를 뒤집어 리턴한다 — 미리 채운 줄


def should_undo(record):                                                     # 기록 한 건을 받는 함수
    """자동 조치가 실제로 바꾼 것이고 해제로 되돌릴 수 있으면 True, 아니면 False 를 리턴한다.
    조치 전부터 그 상태였던 것과 확인에 실패한 조치는 되돌리지 않으려고 쓴다.
    """
    if record["before"] == record["after"]:                                  # 조치 전과 후가 같으면
        return False                                                         # 바뀐 것이 없으니 되돌리지 않는다
    if "확인 실패" in record["after"]:                                       # 확인에 실패한 조치이면 — 미리 채운 줄
        return False                                                         # 실제로 바뀌지 않았으니 되돌리지 않는다 — 미리 채운 줄
    return record["action"] in UNDOABLE_ACTIONS                              # 해제로 되돌릴 수 있는 조치 종류인지의 결과를 리턴한다 — 미리 채운 줄


def rollback_incident(incident_id, log, state):                              # 인시던트 번호 · 기록 리스트 · 연습용 시스템 상태를 받는 함수
    """인시던트의 기록을 거꾸로 훑으며 자동이 바꾼 것만 되돌리고, 되돌릴 수 없는 조치는 따로 기록해 리턴한다.
    조치 전부터 있던 상태를 건드리지 않고 오탐을 복구할 때 쓴다.
    """
    records = []                                                             # 되돌리기 기록을 담을 빈 리스트
    for record in find_incident_records(log, incident_id):                   # 그 인시던트의 기록을 하나씩 꺼낸다
        if should_undo(record):                                              # 자동이 바꾼 것이고 되돌릴 수 있으면
            records.append(undo_record(record, state))                       # 되돌리고 해제 기록을 모은다
        if record["before"] != record["after"] and not should_undo(record):  # 바뀌었는데 되돌릴 수 없는 조치이면 — 미리 채운 줄
            note = "되돌릴 수 없는 조치(" + record["action"] + ") — 사용자가 다시 로그인해야 함"  # 이유 문장을 만들고 — 미리 채운 줄
            records.append(make_record("되돌리기 불가", record["target"], incident_id, record["before"], record["after"], note))  # 기록으로 남긴다 — 미리 채운 줄
    return records                                                           # 되돌리기 기록 리스트를 리턴한다
```

### 🆘 오류가 나면

- `pwd` 가 `soar_response` 로 끝나는지, `ls` 로 <mark>파일 이름이 문서와 같은지</mark> 봅니다.
- `ModuleNotFoundError: No module named 'incident'` 는 <mark style="background:#ffc4d6">월요일에 만든 `incident.py` 가 이 폴더에 없다는 뜻</mark>입니다. `No module named 'rollback'` 은 수요일 파일이 없다는 뜻입니다. 둘 다 위 「🛟 이전 파일이 없을 때」의 코드 상자로 만듭니다.
- 먼저 오류 전체와 내가 친 명령을 AI 에게 붙여 넣어 묻습니다(`.env` · API 키는 지웁니다). 그래도 막히면 맨 아래 「정답」을 봅니다. 그래도 풀리지 않으면 보고서에 「모름 — 막힌 곳: …」 이라고 씁니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 <mark style="background:#ffc4d6">**터미널**에서</mark> 합니다. 실행할 때마다 같은 입력 파일에서 시작해 같은 결과가 나옵니다.

---
# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">2교시 (10:00–10:50) · 어제 근무의 티켓과 조치 기록을 대조해 초동 대응 리포트(incident report) 파일 생성하기</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: <mark style="background:#e0d4ff">어제 6교시 프로그램</mark>은 티켓 7장을 파일로 저장했습니다. 화면에는 근무 중 발생한 사건 · 평균 확인 시간 · 평균 해결 시간 · 응답 기한(SLA)을 넘긴 티켓 수 · 다음 근무자에게 인계할 티켓 목록이 나왔습니다. 오늘 아침 팀장이 「어제 근무의 초동 대응 리포트를 고객사에 보낼 수 있게 파일로 만들어 주세요」라고 요청합니다. **초동 대응**(initial response, 이니셜 리스폰스)은 사건이 발생한 직후 처음 수행한 대응입니다.
> - **문제**: 티켓 파일과 조치 기록 파일이 따로 있어서, 사람이 손으로 옮겨 적으면 누락이 생기기 쉽습니다. 예를 들어 `INC-212`(`yuna` 계정 잠금)는 조치는 실행됐는데 티켓이 없습니다(티켓 추적 누락). <mark style="background:#ffc4d6">티켓만 보고 리포트를 쓰면 이 사건이 누락됩니다.</mark>
> - **부탁**: 티켓 파일은 판다스 표로 바꿔 집계하고, 조치 기록 파일은 티켓과 대조해 리포트 파일 하나로 작성해 주세요. 리포트에는 티켓별 상태 · 탐지 규칙별 티켓 수 · 등급별 평균 확인 시간(MTTA, Mean Time To Acknowledge, 엠티티에이: 티켓 생성부터 담당자가 처음 확인하기까지 걸린 평균 시간) · 응답 기한(SLA)을 넘겨 확인한 티켓 · 티켓이 없는 조치 · 높음 등급 티켓의 처리 경위(생성 → 확인 → 해결 시각을 시간순으로 이은 기록)가 들어갑니다.
> - **바뀌는 점**: 실행 한 번으로 `incident_report_20261112.md` <mark style="background:#bde3ff">32줄</mark>이 생성됩니다. 오늘 샘플에서는 응답 기한(SLA)을 넘겨 확인한 티켓 <mark style="background:#bde3ff">2장</mark>(`TCK-3` · `TCK-4`)과 티켓이 없는 조치 <mark style="background:#bde3ff">1건</mark>(`INC-212`)이 리포트에 따로 적힙니다. 상황과 이름은 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다. (문법 상자의 코드는 눈으로 읽어도 되고, 따라 쳐 보아도 됩니다.)

### 📖 2.1 인시던트 리포트는 「사건 현황 · 평균 확인 시간(MTTA) · 추적 누락 · 처리 경위」를 보고한다

| 리포트의 절 | 읽는 사람이 알고 싶은 것 | 만드는 방법 |
|---|---|---|
| 1. 티켓별 초동 대응 | 사건마다 지금 상태와 조치 기록 수 | 티켓을 한 장씩 읽어 한 줄씩 쓴다 (미리 채움) |
| 2. 규칙별 티켓 수 | 어떤 탐지 규칙의 사건이 많았나 (규칙별 건수) | `value_counts()`(값마다 개수를 세는 판다스 함수) (2 · 8번) |
| 3. 등급별 평균 확인 시간 | 심각도(severity, 시버리티: 사건의 위험 정도) 등급(high 높음 · mid 중간 · low 낮음) 가운데 급한 등급을 빨리 확인했나 | 확인까지 걸린 분 열을 만들고, 확인한 티켓만 필터링해 등급마다 평균 확인 시간(MTTA)을 구한다 (1 · 3 · 4번) |
| 4. 응답 기한을 넘겨 확인한 티켓 | 응답 기한 위반(SLA breach, 에스엘에이 브리치: 약속한 응답 기한을 지키지 못한 일) 티켓은 무엇인가 | <mark style="background:#ffdcb0">`acked_at` 이 `sla_due` 보다 큰</mark> 행(row, 로우: 표의 가로 줄)만 필터링한다 (5번) |
| 5. 티켓이 없는 조치 | 티켓 없이 실행되어 추적에서 누락될 뻔한 조치는 무엇인가 | 조치 기록의 인시던트 번호를 티켓의 인시던트 번호와 대조해, 어느 티켓에도 없는 것을 찾는다 (6 · 7번) |
| 6. 높음(high) 티켓의 처리 경위 | 높음 등급 사건은 어떤 순서로 처리됐는가 | 티켓의 생성 · 확인 · 해결 시각을 시간순으로 이은 한 줄을 만든다(미리 채움) |

- 리포트 파일은 **마크다운**(Markdown, 마크다운: `#` 로 제목, `-` 로 목록을 쓰는 글 형식) 파일입니다. 이 안내 문서도 마크다운입니다. VS Code 에서 열고 `Ctrl+Shift+V`(맥북은 `Cmd+Shift+V`)를 누르면 제목과 목록 모양으로 볼 수 있습니다.
- 아직 확인하지 않은 티켓(미확인, unacknowledged)은 `acked_at` 이 `-1` 입니다. 그대로 빼면 확인까지 걸린 분이 <mark style="background:#ffc4d6">음수</mark>가 됩니다(예: `TCK-2` 는 −1 − 3 = −4분). 이 값이 평균에 들어가면 평균 확인 시간이 실제보다 짧게 계산되므로, 평균을 구하기 전에 <mark style="background:#ffdcb0">`acked_at` 이 0 이상인 행만 필터링</mark>합니다.
- 확인은 했지만 아직 해결하지 않은 티켓(`TCK-4` · `TCK-7`)은 평균에 포함됩니다. 평균 확인 시간은 확인한 시각까지만 측정하는 지표이고, 해결까지 걸린 평균 시간(MTTR, Mean Time To Resolve, 엠티티알)과는 별개이기 때문입니다.

**🐼 판다스 문법 상자 — 그룹마다 평균 `그룹["열"].mean()` 과 반올림 `.round(1)`**

```python
import pandas as pd

table = pd.DataFrame([
    {"grade": "high", "ack_minutes": 10},
    {"grade": "mid", "ack_minutes": 72},
    {"grade": "mid", "ack_minutes": 55},
])
groups = table.groupby("grade")
grade_means = groups["ack_minutes"].mean()
print(grade_means.round(1).to_dict())
```

| 코드 | 뜻 |
|---|---|
| `groups["ack_minutes"].mean()` | <mark style="background:#e0d4ff">4과목에서 배운 `그룹["열"].sum()`</mark> 과 같은 꼴입니다. 합계 대신 그룹마다 평균을 구하는 그룹별 집계입니다. 그룹은 `table.groupby("grade")` 처럼 grade 값이 같은 행끼리 묶은 것입니다 |
| `.round(1)` | 소수 첫째 자리까지 반올림합니다 |
| 위 코드의 출력 | <mark style="background:#bde3ff">`{'high': 10.0, 'mid': 63.5}`</mark> 입니다. mid 는 <mark style="background:#bde3ff">(72 + 55) ÷ 2 = 63.5</mark> 입니다 |

- 4절은 <mark style="background:#ffdcb0">확인 시각(`acked_at`)이 응답 기한 시각(`sla_due`)보다 늦은</mark> 티켓, 즉 SLA 위반 티켓만 집계합니다.
- 오늘 샘플에서 아직 확인하지 않은 티켓은 `TCK-2` · `TCK-5` 입니다. 근무는 180분에 끝났는데 둘의 응답 기한 시각은 243분 · 270분이라서, <mark style="background:#bde3ff">기한이 아직 지나지 않았으므로 위반으로 집계하지 않습니다</mark>.
- `table[table["acked_at"] > table["sla_due"]]` 는 <mark style="background:#e0d4ff">4과목에서 배운</mark> 「조건으로 행 필터링(filtering, 필터링: 조건에 맞는 행만 남기기)하기」와 같은 꼴입니다. 여기서 `table` 은 DataFrame(데이터프레임: 행과 열로 이루어진 판다스의 표)입니다. 조건에 숫자 대신 다른 열을 쓴 것만 다릅니다. 바로 아래 문법 상자에서 작은 예로 확인합니다.

**🐼 판다스 문법 상자 — 두 열로 계산하고 비교하기 `표["열1"] - 표["열2"]` · `표[표["열1"] > 표["열2"]]`**

판다스 표에서 두 열을 같은 행끼리 계산하면 그 결과를 새 열로 추가할 수 있고, 같은 행끼리 비교하면 조건에 맞는 행만 남길 수 있습니다(필터링, filtering). 두 경우 모두 행마다 두 열의 값을 하나씩 확인해서 처리합니다. 아래는 학생 네 명의 수학 · 영어 점수입니다.

```python
import pandas as pd                            # 판다스를 pd 라는 짧은 이름으로 불러온다

data = {                                       # 표에 넣을 내용(열 이름: 값들)
    "name": ["민지", "서준", "하은", "도윤"],  # name 열 (학생 이름)
    "math": [70, 90, 60, 85],                  # math 열 (수학 점수)
    "english": [85, 80, 75, 85],               # english 열 (영어 점수)
}
df = pd.DataFrame(data)                        # 내용으로 표(DataFrame)를 만든다
print(df)                                      # 표를 출력한다
```

실행 결과:

```
  name  math  english
0   민지    70       85
1   서준    90       80
2   하은    60       75
3   도윤    85       85
```

위 코드에 이어서 실행하는 다음 코드입니다. 영어 점수에서 수학 점수를 뺀 열을 만듭니다.

```python
df["gap"] = df["english"] - df["math"]  # 영어 점수에서 수학 점수를 뺀 값을 gap 열로 추가한다
print(df)                               # 열이 하나 늘어난 표를 출력한다
```

실행 결과:

```
  name  math  english  gap
0   민지    70       85   15
1   서준    90       80  -10
2   하은    60       75   15
3   도윤    85       85    0
```

이어서 실행하는 다음 코드입니다. 영어 점수가 수학 점수보다 높은 학생만 남깁니다.

```python
filtered = df[df["english"] > df["math"]]  # 영어 점수가 수학 점수보다 높은 행만 남긴다
print(filtered)                            # 남은 행을 출력한다
```

실행 결과:

```
  name  math  english  gap
0   민지    70       85   15
2   하은    60       75   15
```

| 코드 | 뜻 |
|---|---|
| `df["english"] - df["math"]` | 같은 행끼리 두 열의 값을 뺍니다. 행마다 결과가 하나씩 나옵니다 |
| `df["gap"] = …` | 그 결과를 `gap` 이라는 새 열로 표에 추가합니다 |
| `df["english"] > df["math"]` | 행마다 영어 점수가 수학 점수보다 크면 `True`, 아니면 `False` 입니다 |
| `df[ … ]` | `True` 인 행만 남깁니다 |
| 위 코드의 출력 | <mark style="background:#bde3ff">`민지`(85 > 70) 와 `하은`(75 > 60) 만 남습니다</mark>. `도윤` 은 85 로 같아서 `>` 조건에 맞지 않으므로 빠집니다 |
| 오늘 문제 | 빼기는 `table["acked_at"] - table["created_at"]`(1번), 비교는 `table[table["acked_at"] > table["sla_due"]]`(5번)와 같은 꼴입니다. 확인까지 걸린 분 열을 만들고, 확인 시각이 응답 기한 시각보다 늦은 티켓만 남깁니다 |

함수 일곱 개와 실행 파일 가운데 직접 쓰는 곳은 **아홉 군데**입니다.

```
report.py   make_ticket_table       : 티켓 리스트를 표로 바꾸고 확인까지 걸린 분 열을 더한다 (1번)
            count_by_rule           : 규칙마다 티켓 수를 센다 (2번)
            mean_ack_by_grade       : 확인한 티켓만 남겨 (3번) 등급마다 평균을 구한다 (4번)
            find_late_tickets       : 기한을 넘겨 확인한 티켓만 남긴다 (5번)
            find_missing_incidents  : 티켓이 없는 조치 기록을 찾는다 (6 · 7번)
            count_actions           : 티켓 한 장의 조치 기록 수를 센다 (미리 채움)
            make_timeline_line      : 티켓 한 장의 생성 · 확인 · 해결 시각을 시간순 한 줄로 만든다 (미리 채움)
            make_report_lines       : 리포트의 줄 리스트를 만든다. 규칙별 줄만 직접 쓴다 (8번)
실행 파일   day05_2-1_run.py        : 표를 만들고 (9번), 결과를 출력하고, 리포트 파일을 쓴다 (미리 채움)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 2-1 · 티켓 7장과 조치 기록 10건을 대조해 초동 대응 리포트(incident report) 파일 작성하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>티켓과 조치 기록이 JSON(제이슨: 키와 값으로 적은 데이터 파일 형식) 파일 두 개에 따로 있고, 사람이 읽을 리포트가 없습니다</mark>.
- **만드는 것**: 표 만들기 · 규칙별 수 · 등급별 평균 · 기한 넘긴 티켓 · 티켓 없는 조치 찾기 · 리포트 줄 만들기(`report.py`), 리포트 파일 쓰기(`day05_2-1_run.py`).
- **실행하면**: <mark>단계 1: 불러온 수, 단계 2: 규칙별 티켓 수, 단계 3: 등급별 평균 확인 시간, 단계 4: 기한을 넘긴 티켓과 티켓이 없는 조치, 단계 5: 저장한 리포트 파일이 나옵니다.</mark>

**🎯 할 일**: 두 파일을 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행한 뒤 리포트 파일을 열어 읽습니다.

**`report.py`** — 리포트를 만드는 함수 모음입니다. 직접 쓰는 곳은 1 ~ 8번입니다.

```python
import pandas as pd                                                                        # 표를 다루기 위해 판다스를 pd 라는 이름으로 불러온다

REPORT_TITLE = "# 초동 대응 리포트 — 2026-11-12(목) 오전 근무"                             # 리포트 맨 위 제목


def make_ticket_table(tickets):                                                            # 티켓 리스트를 받는 함수
    """티켓 리스트를 표(DataFrame)로 바꾸고, 확인까지 걸린 분(ack_minutes) 열을 더해 리턴한다.
    티켓마다 담당자가 얼마나 빨리 확인했는지를 표 하나로 계산할 때 쓴다.
    """
    table = pd.DataFrame(tickets)                                                          # 티켓 리스트를 표로 바꾼다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. table["acked_at"] - table["created_at"] 를 table["ack_minutes"] 에 저장한다 (확인까지 걸린 분)
    return table                                                                           # 열을 더한 표를 리턴한다 — 미리 채운 줄


def count_by_rule(table):                                                                  # 티켓 표를 받는 함수
    """탐지 규칙마다 티켓이 몇 장인지 세어 딕셔너리로 리턴한다.
    어떤 규칙의 사건이 많았는지 리포트 첫머리에 보여 줄 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. table["rule"].value_counts() 를 rule_counts 에 저장한다
    return rule_counts.to_dict()                                                           # 센 결과를 딕셔너리로 바꿔 리턴한다 — 미리 채운 줄


def mean_ack_by_grade(table):                                                              # 티켓 표를 받는 함수
    """확인한 티켓만 남겨 등급마다 확인까지 걸린 분의 평균을 구하고, 소수 첫째 자리까지 딕셔너리로 리턴한다.
    급한 등급일수록 빨리 확인했는지 리포트로 보여 줄 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. table["acked_at"] >= 0 인 행만 남겨 acked 에 저장한다 (확인한 티켓만)
    groups = acked.groupby("grade")                                                        # 등급이 같은 행끼리 묶는다 — 미리 채운 줄
    # 4. groups["ack_minutes"].mean() 을 grade_means 에 저장한다 (등급마다 평균)
    rounded = grade_means.round(1)                                                         # 소수 첫째 자리까지 반올림한다 — 미리 채운 줄
    return rounded.to_dict()                                                               # 등급별 평균을 딕셔너리로 바꿔 리턴한다 — 미리 채운 줄


def find_late_tickets(table):                                                              # 티켓 표를 받는 함수
    """응답 기한 시각(sla_due)보다 늦게 확인한 티켓을 딕셔너리 리스트로 리턴한다.
    응답 기한을 넘긴 티켓을 리포트에 이름으로 남길 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. table["acked_at"] > table["sla_due"] 인 행만 남겨 late 에 저장한다
    return late.to_dict("records")                                                         # 남은 행을 딕셔너리 리스트로 바꿔 리턴한다 — 미리 채운 줄


def find_missing_incidents(actions, tickets):                                              # 조치 기록 리스트와 티켓 리스트를 받는 함수
    """조치 기록 가운데 어느 티켓에도 들어 있지 않은 인시던트의 기록을 리스트로 리턴한다.
    조치는 했는데 티켓이 없어 리포트에서 빠지는 사건을 찾을 때 쓴다.
    """
    covered = []                                                                           # 티켓에 들어 있는 인시던트 번호를 모을 빈 리스트 — 미리 채운 줄
    for ticket in tickets:                                                                 # 티켓을 하나씩 읽는다 — 미리 채운 줄
        for incident_id in ticket["incidents"]:                                            # 티켓에 합쳐진 인시던트 번호를 하나씩 읽는다 — 미리 채운 줄
            covered.append(incident_id)                                                    # 번호를 추가한다 — 미리 채운 줄
    missing = []                                                                           # 티켓이 없는 조치 기록을 모을 빈 리스트 — 미리 채운 줄
    for action in actions:                                                                 # 조치 기록을 하나씩 읽는다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 6. action["incident"] 가 covered 안에 없으면 (if, not in)
            # 7. missing 에 action 을 추가한다 (append)
    return missing                                                                         # 티켓이 없는 조치 기록 리스트를 리턴한다 — 미리 채운 줄


def count_actions(ticket, actions):                                                        # 티켓 한 장과 조치 기록 리스트를 받는 함수
    """티켓에 합쳐진 인시던트의 조치 기록이 몇 건인지 세어 리턴한다.
    리포트의 티켓 줄에 조치 기록 수를 함께 적을 때 쓴다.
    """
    count = 0                                                                              # 조치 기록 수 : 처음에는 0
    for action in actions:                                                                 # 조치 기록을 하나씩 읽는다
        if action["incident"] in ticket["incidents"]:                                      # 이 티켓의 인시던트 기록이면
            count = count + 1                                                              # 1 늘린다
    return count                                                                           # 센 수를 리턴한다


def make_timeline_line(ticket):                                                            # 티켓 한 장을 받는 함수
    """티켓 한 장의 생성 · 확인 · 해결 시각을 시간순으로 이은 한 줄을 리턴한다.
    높음 등급 사건이 어떤 순서로 처리됐는지 리포트에 처리 경위로 남길 때 쓴다.
    """
    steps = [str(ticket["created_at"]) + "분 티켓 생성"]                                   # 생성 시각으로 시작한다
    if ticket["acked_at"] >= 0:                                                            # 확인했으면 (확인 전이면 -1)
        steps.append(str(ticket["acked_at"]) + "분 담당자 확인")                           # 확인 시각을 추가한다
    if ticket["resolved_at"] >= 0:                                                         # 해결했으면 (해결 전이면 -1)
        steps.append(str(ticket["resolved_at"]) + "분 해결")                               # 해결 시각을 추가한다
    return "- " + ticket["id"] + " · " + ticket["entity"] + ": " + " → ".join(steps)       # 시각을 화살표로 이어 한 줄로 리턴한다


def make_report_lines(tickets, actions, rule_counts, grade_means, late_tickets, missing):  # 리포트에 넣을 재료를 받는 함수
    """리포트에 넣을 재료로 마크다운 문서의 줄 리스트를 만들어 리턴한다.
    근무가 끝난 뒤 사람이 읽을 초동 대응 리포트를 자동으로 쓸 때 쓴다.
    """
    lines = [REPORT_TITLE, ""]                                                             # 제목과 빈 줄로 시작한다 — 미리 채운 줄
    lines.append("## 1. 티켓별 초동 대응")                                                 # 1절 제목 — 미리 채운 줄
    for ticket in tickets:                                                                 # 티켓을 하나씩 읽는다 — 미리 채운 줄
        action_count = count_actions(ticket, actions)                                      # 이 티켓의 조치 기록 수 — 미리 채운 줄
        head = "- " + ticket["id"] + " [" + ticket["grade"] + "] " + ticket["entity"] + " — " + ticket["rule"]  # 티켓 번호 · 등급 · 대상 · 규칙 — 미리 채운 줄
        lines.append(head + " · 상태 " + ticket["status"] + " · 조치 기록 " + str(action_count) + "건")  # 티켓 한 줄을 추가한다 — 미리 채운 줄
    lines.append("")                                                                       # 빈 줄 — 미리 채운 줄
    lines.append("## 2. 규칙별 티켓 수")                                                   # 2절 제목 — 미리 채운 줄
    for rule in rule_counts:                                                               # 규칙 이름을 하나씩 읽는다 — 미리 채운 줄
        count = rule_counts[rule]                                                          # 그 규칙의 티켓 수 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 8. "- " + rule + ": " + str(count) + "장" 을 lines 에 추가한다 (append)
    lines.append("")                                                                       # 빈 줄 — 미리 채운 줄
    lines.append("## 3. 등급별 평균 확인 시간(분)")                                        # 3절 제목 — 미리 채운 줄
    for grade in grade_means:                                                              # 등급을 하나씩 읽는다 — 미리 채운 줄
        lines.append("- " + grade + ": " + str(grade_means[grade]) + "분")                 # 등급 한 줄을 추가한다 — 미리 채운 줄
    lines.append("")                                                                       # 빈 줄 — 미리 채운 줄
    lines.append("## 4. 응답 기한을 넘겨 확인한 티켓")                                     # 4절 제목 — 미리 채운 줄
    for ticket in late_tickets:                                                            # 늦게 확인한 티켓을 하나씩 읽는다 — 미리 채운 줄
        lines.append("- " + ticket["id"] + " · 기한 " + str(ticket["sla_due"]) + "분 · 확인 " + str(ticket["acked_at"]) + "분")  # 티켓 한 줄을 추가한다 — 미리 채운 줄
    lines.append("")                                                                       # 빈 줄 — 미리 채운 줄
    lines.append("## 5. 티켓이 없는 조치 (사람이 티켓을 만들어야 함)")                     # 5절 제목 — 미리 채운 줄
    for action in missing:                                                                 # 티켓이 없는 조치 기록을 하나씩 읽는다 — 미리 채운 줄
        lines.append("- " + action["incident"] + " · " + action["action"] + " · " + action["target"])  # 기록 한 줄을 추가한다 — 미리 채운 줄
    lines.append("")                                                                       # 빈 줄 — 미리 채운 줄
    lines.append("## 6. 높음(high) 티켓의 처리 경위")                                      # 6절 제목 — 미리 채운 줄
    for ticket in tickets:                                                                 # 티켓을 하나씩 읽는다 — 미리 채운 줄
        if ticket["grade"] == "high":                                                      # 높음 등급 티켓이면 — 미리 채운 줄
            lines.append(make_timeline_line(ticket))                                       # 처리 경위 한 줄을 추가한다 — 미리 채운 줄
    return lines                                                                           # 완성한 줄 리스트를 리턴한다 — 미리 채운 줄
```

**`day05_2-1_run.py`** — 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다.

```python
from incident import load_json                                                                # 월요일 파일의 JSON 읽기 함수를 불러온다
from report import make_ticket_table, count_by_rule, mean_ack_by_grade, find_late_tickets, find_missing_incidents, make_report_lines  # 방금 만든 리포트 함수를 불러온다

REPORT_PATH = "incident_report_20261112.md"                                                   # 리포트를 저장할 파일 이름

tickets = load_json("day05_tickets.json")                                                     # 목요일 근무의 티켓 파일을 리스트로 읽는다
actions = load_json("day05_actions.json")                                                     # 목요일 근무의 조치 기록 파일을 리스트로 읽는다
print("--- 단계 1: 불러온 티켓", len(tickets), "장 · 조치 기록", len(actions), "건")          # 단계 1 시작을 알리는 줄

# ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
# 9. make_ticket_table(tickets) 의 결과를 table 에 저장한다
rule_counts = count_by_rule(table)                                                            # 규칙별 티켓 수
grade_means = mean_ack_by_grade(table)                                                        # 등급별 평균 확인 시간
late_tickets = find_late_tickets(table)                                                       # 응답 기한을 넘겨 확인한 티켓
missing = find_missing_incidents(actions, tickets)                                            # 티켓이 없는 조치 기록

print("--- 단계 2: 규칙별 티켓 수")                                                           # 단계 2 시작을 알리는 줄
for rule in rule_counts:                                                                      # 규칙 이름을 하나씩 읽는다
    print(rule, ":", rule_counts[rule], "장")                                                 # 규칙과 티켓 수를 출력한다

print("--- 단계 3: 등급별 평균 확인 시간(분)")                                                # 단계 3 시작을 알리는 줄
for grade in grade_means:                                                                     # 등급을 하나씩 읽는다
    print(grade, ":", grade_means[grade], "분")                                               # 등급과 평균을 출력한다

print("--- 단계 4: 응답 기한을 넘겨 확인한 티켓", len(late_tickets), "장 · 티켓이 없는 조치", len(missing), "건")  # 단계 4 시작을 알리는 줄
for ticket in late_tickets:                                                                   # 늦게 확인한 티켓을 하나씩 읽는다
    print(ticket["id"], "기한", ticket["sla_due"], "분 · 확인", ticket["acked_at"], "분")     # 티켓과 두 시각을 출력한다
for action in missing:                                                                        # 티켓이 없는 조치 기록을 하나씩 읽는다
    print(action["incident"], action["action"], action["target"], "→ 티켓 없음")              # 기록을 출력한다

lines = make_report_lines(tickets, actions, rule_counts, grade_means, late_tickets, missing)  # 리포트 줄 리스트를 만든다
text = "\n".join(lines) + "\n"                                                                # 줄 리스트를 줄바꿈으로 이어 한 문자열로 만든다
with open(REPORT_PATH, "w", encoding="utf-8") as report_file:                                 # 리포트 파일을 쓰기 모드("w")로 연다
    report_file.write(text)                                                                   # 리포트 문자열을 파일에 쓴다
print("--- 단계 5: 리포트 파일", REPORT_PATH, "·", len(lines), "줄 저장")                     # 단계 5 시작을 알리는 줄과 저장한 줄 수
```

**순서**

1. **[터미널]** 파일 두 개를 만들고 **[VS Code]** 에서 열어 붙여 넣습니다.
   ```bash
   pwd
   touch report.py day05_2-1_run.py
   ls
   ```
2. **[VS Code]** `report.py` 1 ~ 8번, `day05_2-1_run.py` 9번을 씁니다. 막히면 위 문법 상자와 아래 「2교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 가 `soar_response` 로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   python day05_2-1_run.py
   ```
4. 출력은 다섯 단계입니다. 제목 줄은 줄 수에 넣지 않습니다.
   - 단계 1 과 단계 5 는 숫자가 제목 줄에 함께 나와 그 아래 줄이 없습니다.
   - 단계 2 는 5줄, 단계 3 은 2줄입니다.
   - 단계 4 는 숫자가 제목 줄에 함께 나오고 그 아래 3줄입니다.
5. **[VS Code]** 왼쪽 목록에서 `incident_report_20261112.md` 를 열고 `Ctrl+Shift+V`(맥북은 `Cmd+Shift+V`)로 모양을 봅니다. <mark>1 ~ 6절이 보이면</mark> 됩니다.
6. **[보고서]** `day05_am_report.md` 의 `## 2교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 티켓이 가장 많은 규칙 두 개와 리포트 파일의 줄 수를 적어 주세요.
   - (나) 🔍 단계 3 에 low 등급이 없습니다. `day05_tickets.json` 의 low 티켓 두 장(`TCK-2` · `TCK-5`)의 `acked_at` 을 근거로 그 이유를 적어 주세요. 또 `report.py` 3번(확인한 티켓만 필터링하는 줄)이 없으면 low 의 평균 확인 시간(MTTA)이 얼마로 나오는지도 적어 주세요.
   - (다) 🔍 리포트 5절에 `INC-212` 가 나왔습니다. `find_missing_incidents` 의 `covered` 리스트를 근거로 그 이유를 적고, 이 절이 없으면 고객사에 보내는 리포트에서 어떤 사건이 추적 누락되는지 적어 주세요.

### 2교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 두 열을 빼서 새 열 만들기 | `table["ack_minutes"] = table["acked_at"] - table["created_at"]` |
| 값마다 개수 세기 | `rule_counts = table["rule"].value_counts()` |
| 조건으로 행 필터링하기 | `acked = table[table["acked_at"] >= 0]` |
| 등급이 같은 행끼리 그룹으로 나누고 그룹마다 평균 | `groups = acked.groupby("grade")` → `grade_means = groups["ack_minutes"].mean()` |
| 다른 열과 비교해 행 필터링하기 | `late = table[table["acked_at"] > table["sla_due"]]` |
| 리스트에 없으면 | `if action["incident"] not in covered:` |
| 리스트에 추가 | `missing.append(action)` |
| 문자열을 이어 붙여 추가 | `lines.append("- " + rule + ": " + str(count) + "장")` |
| 함수 결과를 변수에 저장하기 | `table = make_ticket_table(tickets)` |

---
# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">3교시 (11:00–11:50) · 조치 요청마다 위험 점수(risk score)를 합산해 자동 · 승인 필요 · 차단 금지로 분류하기 (승인 게이트, human-in-the-loop)</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: <mark style="background:#e0d4ff">월요일에는 플레이북</mark>(playbook, 플레이북: 사건 종류별로 미리 정한 대응 순서)마다 승인 값을 하나(`자동` 또는 `담당자 승인 필요`)씩 정했습니다. <mark style="background:#e0d4ff">화요일에는</mark> 「VIP(브이아이피: 막히면 업무에 큰 영향을 주는 중요한 계정) 이면 승인 필요」를 `decide_route` 함수 안의 조건문으로 작성했습니다(승인 여부를 정하는 규칙이 코드 안에 있어서, 규칙을 바꾸려면 코드를 수정해야 하는 방식). 오늘 아침 자동 대응이 실행하려는 조치 요청 8건이 들어왔습니다.
> - **문제**: 같은 계정 잠금이라도 위험이 다릅니다. 퇴사자 한 명(`REQ-1` `dami`)을 잠그는 것과 계정 6개를 한꺼번에 잠그는 것(`REQ-6`)은 잘못 실행했을 때 업무에 미치는 피해의 범위(영향 범위)가 다릅니다. <mark style="background:#ffc4d6">그런데 승인 값은 플레이북 하나에 하나뿐이어서 요청마다 위험에 맞게 다르게 정할 수 없습니다.</mark> 또 「공유 IP(여러 계정이 함께 쓰는 IP)도 승인을 받자」처럼 기준을 바꾸려면 코드를 수정해야 합니다.
> - **부탁**: 승인 기준을 설정 파일 `config/approval_policy.json` 으로 분리하고, 요청마다 위험 점수를 합산해 「자동 · 승인 필요 · 차단 금지」 가운데 하나로 분류해 주세요. 허용 목록(allowlist, 얼라우리스트: 차단 대상에서 제외하기로 미리 정한 IP 의 목록) 대상은 <mark style="background:#ffc4d6">점수와 상관없이 차단 금지</mark>입니다.
> - **바뀌는 점**: 8건이 <mark style="background:#bde3ff">자동 3건 · 승인 필요 3건 · 차단 금지 2건</mark>으로 분류되고, 결정마다 점수를 합산한 근거가 함께 출력됩니다. 상황과 숫자는 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다.

### 📖 3.1 승인 게이트는 「허용 목록 확인 → 위험 점수 합산 → 임계값 비교」 순서로 판단한다

**승인 게이트**(approval gate, 어프루벌 게이트: 자동 대응이 조치를 실행하기 직전에, 바로 실행할지 사람의 승인을 받을지 정하는 단계)는 사람 개입 방식(human-in-the-loop, 휴먼 인 더 루프: 자동화 흐름 중간에 사람이 판단하고 승인하는 방식)를 구현하는 통제 지점입니다. 위험이 낮은 조치는 자동으로 실행하고, 위험이 큰 조치만 사람에게 승인을 요청합니다. 판단 순서는 아래와 같습니다.

| 순서 | 확인 | 결과 |
|---|---|---|
| 1 | 대상이 허용 목록(`allowlist_ips`)에 있는가 | 있으면 점수를 보지 않고 **차단 금지** |
| 2 | 위험 점수를 합산한다 | 합산하는 점수: <mark style="background:#ffdcb0">등급(high 2점 · mid 1점 · low 0점), VIP 계정 3점, 함께 쓰는 IP(공유 IP) 2점, 대상 4개 이상 2점</mark> |
| 3 | 점수가 임계값(threshold, 쓰레숄드: 판정이 바뀌는 기준 점수) <mark style="background:#ffdcb0">`approval_score`(3) 이상</mark>인가 | 이상이면 **승인 필요**, 아니면 **자동** |

- 허용 목록(allowlist)은 차단 대상에서 제외하기로 미리 정해 둔 IP 의 목록입니다. 오늘은 협력사 사무실 IP `203.0.113.80` 과 점검 서버 `192.0.2.10` 이 있습니다.
- <mark>허용 목록을 점수보다 먼저 판단합니다.</mark> 차단하면 업무가 중단되는 IP 는 위험 점수와 무관하게 차단하지 않는 것이 원칙이기 때문입니다.
- 공유 IP(함께 쓰는 IP, shared IP)는 그 IP 를 쓰는 계정이 <mark style="background:#ffdcb0">2개 이상(`shared_ip_limit`)</mark>인 경우입니다. <mark style="background:#e0d4ff">수요일에 「여러 계정이 함께 쓰는 IP 라서 담당자 승인 필요」로 처리하던 규칙</mark>을 점수로 바꾼 것입니다.
- 대상 수는 요청 하나가 한꺼번에 조치하는 대상(계정 또는 IP)의 수이고, 잘못 실행했을 때 영향이 미치는 범위(영향 범위)를 나타냅니다. <mark style="background:#e0d4ff">화요일에는 한 번에 3개를 넘게 잠그지 못하도록 차단했습니다.</mark> 오늘은 차단하는 대신, <mark style="background:#ffdcb0">3개를 넘으면 위험 점수 2점을 더해</mark> 사람이 승인하게 바꿨습니다.
- 업계에서 자동 조치와 승인 필요 조치를 나눌 때는 <mark>가역성 · 영향 범위 · 확실성</mark> 세 가지를 봅니다. 가역성(reversibility)은 조치를 되돌릴 수 있는 정도, 영향 범위는 조치가 미치는 계정 · IP 의 범위, 확실성은 탐지가 진짜 공격일 가능성이 확실한 정도입니다. 오늘의 위험 점수는 영향 범위를 VIP 계정 · 공유 IP · 대상 수로, 확실성을 허용 목록 확인(정상임이 확실한 대상은 차단 금지)으로 나타내고, 탐지 등급은 사건의 심각도로 점수에 더합니다. 가역성은 점수에 넣지 않았습니다. 계정 잠금과 IP 차단은 수요일에 되돌리기(롤백)를 만들었고, 되돌릴 수 없는 세션 종료는 오후 5교시의 리스크 평가에서 다룹니다.
- 점수와 기준은 모두 `config/approval_policy.json` 에 있습니다. 코드에는 점수를 합산하는 로직만 작성하고, <mark>합산할 점수 값은 설정 파일에 분리</mark>해 둡니다. 그래서 정책을 바꿀 때 코드를 수정하지 않고 설정 파일만 바꾸면 됩니다.

함수 세 개와 실행 파일 가운데 직접 쓰는 곳은 **아홉 군데**입니다.

```
approval_gate.py   is_allowlisted  : 대상이 허용 목록에 있는지 리턴한다 (1번)
                   risk_score      : 등급 점수로 시작해 (2번), VIP 이면 (3번) 점수를 더한다 (4번). 함께 쓰는 IP · 대상 수는 미리 채움
                   decide_gate     : 허용 목록이면 차단 금지 (5번), 점수를 받아 (6번), 기준 이상이면 승인 필요 (7번)
실행 파일          day05_3-1_run.py : 요청마다 결정을 받아 (8번) 결정별로 센다 (9번)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 3-1 · 조치 요청 8건을 위험 점수 합산으로 자동 · 승인 필요 · 차단 금지로 분류하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>승인이 필요한지는 플레이북마다 정한 값 하나로만 정해지고, 기준이 코드 안에 있습니다</mark>.
- **만드는 것**: 허용 목록 확인 · 위험 점수 · 결정(`approval_gate.py`), 요청마다 결정하고 세기(`day05_3-1_run.py`).
- **실행하면**: <mark>단계 1: 불러온 요청 수와 기준 점수, 단계 2: 요청마다 결정과 이유, 단계 3: 결정별 요청 수, 단계 4: 담당자에게 보낼 승인 요청, 단계 5: 저장한 결정 수가 나옵니다.</mark>

**🎯 할 일**: 데이터 파일 두 개와 코드 파일 두 개를 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행해서 단계 2 ~ 4 를 읽습니다.

**`config/approval_policy.json`** — 승인 게이트의 기준입니다. 점수 값은 위 3.1 표와 같습니다. 코드는 이 파일의 키 이름으로 읽습니다.

```
{
  "allowlist_ips": ["203.0.113.80", "192.0.2.10"],
  "vip_accounts": ["gaeun"],
  "grade_points": {"high": 2, "mid": 1, "low": 0},
  "vip_points": 3,
  "shared_ip_points": 2,
  "shared_ip_limit": 2,
  "many_targets_points": 2,
  "many_targets_limit": 3,
  "approval_score": 3
}
```

**`gate_requests.json`** — 오늘 아침 자동 대응이 실행하려는 조치 요청 8건입니다. `users_on_ip` 는 그 IP 를 쓰는 계정 수(계정 조치면 0), `target_count` 는 요청 하나가 한꺼번에 조치하는 대상 수입니다.

```
[
  {"id": "REQ-1", "incident": "INC-311", "action": "계정 잠금", "target": "dami", "grade": "high", "users_on_ip": 0, "target_count": 1},
  {"id": "REQ-2", "incident": "INC-312", "action": "계정 잠금", "target": "gaeun", "grade": "mid", "users_on_ip": 0, "target_count": 1},
  {"id": "REQ-3", "incident": "INC-313", "action": "IP 차단", "target": "203.0.113.80", "grade": "high", "users_on_ip": 4, "target_count": 1},
  {"id": "REQ-4", "incident": "INC-314", "action": "IP 차단", "target": "198.51.100.45", "grade": "low", "users_on_ip": 0, "target_count": 1},
  {"id": "REQ-5", "incident": "INC-315", "action": "IP 차단", "target": "198.51.100.77", "grade": "mid", "users_on_ip": 3, "target_count": 1},
  {"id": "REQ-6", "incident": "INC-316", "action": "계정 잠금", "target": "minsu", "grade": "high", "users_on_ip": 0, "target_count": 6},
  {"id": "REQ-7", "incident": "INC-317", "action": "세션 종료", "target": "hana", "grade": "mid", "users_on_ip": 0, "target_count": 1},
  {"id": "REQ-8", "incident": "INC-318", "action": "IP 차단", "target": "192.0.2.10", "grade": "low", "users_on_ip": 1, "target_count": 1}
]
```

**`approval_gate.py`** — 승인 게이트 함수 모음입니다. 6교시도 가져와 사용(import)합니다. 직접 쓰는 곳은 1 ~ 7번입니다.

- 3번 아래에는 `if` 한 줄을 씁니다. 그 아래 미리 채운 `reasons.append(…)` 줄은 4번과 함께 `if` 안쪽입니다.
- 5번과 7번도 `if` 한 줄만 씁니다. 그 아래 미리 채운 `return` 줄이 `if` 안쪽입니다.

```python
def is_allowlisted(request, policy):                                        # 조치 요청 한 건과 승인 정책을 받는 함수
    """조치 대상이 허용 목록에 있으면 True, 없으면 False 를 리턴한다.
    협력사 사무실이나 점검 서버처럼 지금 정책에서 차단하지 않기로 등록한 대상을 먼저 가려낼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. request["target"] 이 policy["allowlist_ips"] 안에 있는지(in)의 결과를 리턴한다


def risk_score(request, policy):                                            # 조치 요청 한 건과 승인 정책을 받는 함수
    """등급 · VIP · 함께 쓰는 IP · 대상 수로 위험 점수를 더하고, 점수와 이유 리스트를 함께 리턴한다.
    자동으로 실행해도 되는 요청인지 숫자로 판단할 때 쓴다.
    """
    grade_table = policy["grade_points"]                                    # 등급마다 정한 점수 표 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. grade_table[request["grade"]] 를 score 에 저장한다 (등급 점수로 시작한다)
    reasons = ["등급 " + request["grade"] + " +" + str(score)]              # 점수를 더한 이유 리스트 — 미리 채운 줄
    # 3. request["target"] 이 policy["vip_accounts"] 안에 있으면 (if, in)
        # 4. score 에 score + policy["vip_points"] 를 저장한다 (VIP 점수를 더한다)
        reasons.append("VIP 계정 +" + str(policy["vip_points"]))            # 이유를 추가한다 — 미리 채운 줄
    if request["users_on_ip"] >= policy["shared_ip_limit"]:                 # 여러 계정이 함께 쓰는 IP 이면 — 미리 채운 줄
        score = score + policy["shared_ip_points"]                          # 함께 쓰는 IP 점수를 더한다 — 미리 채운 줄
        reasons.append("함께 쓰는 IP +" + str(policy["shared_ip_points"]))  # 이유를 추가한다 — 미리 채운 줄
    if request["target_count"] > policy["many_targets_limit"]:              # 한 번에 조치할 대상이 많으면 — 미리 채운 줄
        score = score + policy["many_targets_points"]                       # 대상 수 점수를 더한다 — 미리 채운 줄
        reasons.append("대상 " + str(request["target_count"]) + "개 +" + str(policy["many_targets_points"]))  # 이유를 추가한다 — 미리 채운 줄
    return score, reasons                                                   # 점수와 이유 리스트를 함께 리턴한다 — 미리 채운 줄


def decide_gate(request, policy):                                           # 조치 요청 한 건과 승인 정책을 받는 함수
    """조치 요청 한 건을 「차단 금지」 · 「승인 필요」 · 「자동」 가운데 하나로 정하고, 결정과 이유 리스트를 함께 리턴한다.
    자동 대응이 조치를 실행하기 직전에, 사람의 승인이 필요한지 정할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. is_allowlisted(request, policy) 가 참이면 (if)
        return "차단 금지", ["허용 목록 대상"]                              # 결정과 이유를 함께 리턴한다 — 미리 채운 줄
    # 6. risk_score(request, policy) 의 두 결과를 score, reasons 에 저장한다
    reasons.append("합계 " + str(score) + "점")                             # 합계 점수를 이유에 추가한다 — 미리 채운 줄
    # 7. score 가 policy["approval_score"] 이상이면 (if, >=)
        return "승인 필요", reasons                                         # 결정과 이유를 함께 리턴한다 — 미리 채운 줄
    return "자동", reasons                                                  # 기준보다 낮으면 자동으로 실행한다 — 미리 채운 줄
```

**`day05_3-1_run.py`** — 8 · 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다.

```python
from incident import load_json, save_json                           # 월요일 파일의 JSON 읽기 · 쓰기 함수를 불러온다
from approval_gate import decide_gate                               # 방금 만든 승인 게이트 함수를 불러온다

policy = load_json("config/approval_policy.json")                   # 승인 정책 파일을 딕셔너리로 읽는다
requests = load_json("gate_requests.json")                          # 오늘 들어온 조치 요청 파일을 리스트로 읽는다
print("--- 단계 1: 불러온 조치 요청", len(requests), "건 · 승인 기준", policy["approval_score"], "점")  # 단계 1 시작을 알리는 줄

counts = {"자동": 0, "승인 필요": 0, "차단 금지": 0}                # 결정마다 요청 수 : 처음에는 모두 0
results = []                                                        # 요청마다 결정을 저장할 빈 리스트
print("--- 단계 2: 요청마다 결정과 이유")                           # 단계 2 시작을 알리는 줄
for request in requests:                                            # 조치 요청을 하나씩 읽는다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 8. decide_gate(request, policy) 의 두 결과를 decision, reasons 에 저장한다
    # 9. counts[decision] 에 counts[decision] + 1 을 저장한다 (1 늘린다)
    reason_text = ", ".join(reasons)                                # 이유 리스트를 쉼표로 이어 한 문자열로 만든다
    print(request["id"], request["action"], request["target"], "→", decision, "·", reason_text)  # 요청과 결정을 출력한다
    results.append({"id": request["id"], "incident": request["incident"], "action": request["action"], "target": request["target"], "decision": decision})  # 결정을 추가한다

print("--- 단계 3: 결정별 요청 수")                                 # 단계 3 시작을 알리는 줄
for decision in counts:                                             # 결정 이름을 하나씩 읽는다
    print(decision, ":", counts[decision], "건")                    # 결정과 요청 수를 출력한다

print("--- 단계 4: 담당자에게 보낼 승인 요청")                      # 단계 4 시작을 알리는 줄
for result in results:                                              # 결정을 하나씩 읽는다
    if result["decision"] == "승인 필요":                           # 사람의 승인이 필요하면
        print(result["id"], result["incident"], result["action"], result["target"], "→ 담당자 승인을 기다림")  # 승인 요청을 출력한다

save_json(results, "gate_results.json")                             # 결정 리스트를 파일에 저장한다
print("--- 단계 5: gate_results.json 에", len(results), "건 저장")  # 단계 5 시작을 알리는 줄과 저장한 수
```

**순서**

1. **[터미널]** 파일 네 개를 만들고 **[VS Code]** 에서 열어 붙여 넣습니다.
   ```bash
   pwd
   mkdir -p config
   touch config/approval_policy.json gate_requests.json approval_gate.py day05_3-1_run.py
   ls config
   ```
   - 명령 풀이: `mkdir -p config` 는 `config` 폴더가 없을 때만 만듭니다(이미 있으면 그대로 둡니다).
2. **[VS Code]** `approval_gate.py` 1 ~ 7번, `day05_3-1_run.py` 8 · 9번을 씁니다. 막히면 아래 「3교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 가 `soar_response` 로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   python day05_3-1_run.py
   ```
4. 출력은 다섯 단계입니다. 제목 줄은 줄 수에 넣지 않습니다.
   - 단계 1 과 단계 5 는 숫자가 제목 줄에 함께 나와 그 아래 줄이 없습니다.
   - 단계 2 는 8줄, 단계 3 은 3줄, 단계 4 는 3줄입니다.
5. **[보고서]** `day05_am_report.md` 의 `## 3교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 결정별 요청 수를 적고, 승인 필요인 요청 번호도 적어 주세요.
   - (나) 🔍 `REQ-1`(`dami`)과 `REQ-6`(`minsu`)은 둘 다 high 등급의 계정 잠금인데 결정이 다릅니다. 단계 2 의 이유를 근거로 결정이 달라진 이유를 적어 주세요. 그리고 대상 수(영향 범위)를 위험 점수에 반영해야 하는 이유도 적어 주세요.
   - (다) 🔍 `REQ-3` 은 high 등급이고 함께 쓰는 IP 인데 차단 금지입니다. `decide_gate` 가 허용 목록을 점수보다 먼저 확인하는 이유를 적고, 승인 기준(임계값)을 코드가 아니라 설정 파일로 분리하면 무엇이 좋은지 적어 주세요.

### 3교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 리스트 안에 있는지의 결과 리턴 | `return request["target"] in policy["allowlist_ips"]` |
| 딕셔너리에서 값을 읽어 변수에 저장하기 | `score = grade_table[request["grade"]]` |
| 리스트 안에 있으면 | `if request["target"] in policy["vip_accounts"]:` |
| 더해서 다시 저장하기 | `score = score + policy["vip_points"]` |
| 함수 결과가 참이면 | `if is_allowlisted(request, policy):` |
| 두 결과를 함께 받기 | `score, reasons = risk_score(request, policy)` |
| 기준 이상이면 | `if score >= policy["approval_score"]:` |
| 1 늘려 다시 저장하기 | `counts[decision] = counts[decision] + 1` |

---
# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">4교시 (12:00–12:50) · 오탐(false positive) 신고를 받아 영향 확인 · 롤백 · 복구 확인 · 규칙 조정 제안까지 처리하기</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: <mark style="background:#e0d4ff">수요일에 자동 조치를 원래 상태로 복원(롤백, rollback)하는 `rollback_incident` 를 만들었습니다.</mark> 오늘 오전 **오탐**(false positive, 폴스 포지티브: 정상 활동을 공격으로 잘못 판정한 것) 신고가 2건 들어왔습니다.
>   - `INC-301`: 해외 IP 에서 로그인한 `jiwoo` 계정을 자동으로 잠그고 세션(session, 세션: 로그인한 뒤 서버가 유지하는 접속 상태)을 종료했는데, 영업팀장이 「출장 중이고 출장 등록도 했다」고 알려 왔습니다.
>   - `INC-202`: 경로 스캔(서버의 여러 주소에 차례로 요청을 보내 약점을 찾는 일)으로 자동 차단한 IP `198.51.100.90` 이 회사가 계약한 점검 업체의 스캐너라고 인프라팀이 알려 왔습니다.
> - **문제**: 롤백 함수만 실행하면 오탐 대응이 끝나지 않습니다. <mark style="background:#ffc4d6">영향 확인(impact assessment: 조치가 실제로 바꾼 대상을 파악하는 일)을 먼저 하지 않으면</mark> 누가 영향을 받았는지 알 수 없습니다. 신고와 상관없는 진짜 공격(정탐, true positive: 실제 공격을 정확히 탐지한 것)인 `dami` 잠금(`INC-201`)이 그대로인지도 따로 확인하기 어렵습니다. 롤백한 뒤 복구 확인(recovery verification: 실제 상태가 복원됐는지 다시 점검하는 일)을 하지 않으면 해제되지 않은 계정이 남아도 알 수 없어, `jiwoo` 가 계속 로그인하지 못할 수 있습니다. 탐지 규칙을 조정하지 않으면 다음 출장 때도 같은 오탐 알림이 생깁니다.
> - **부탁**: 오탐 신고마다 영향 확인 → 롤백 → 복구 확인 순서로 처리하고, 신고를 접수한 뒤 <mark style="background:#ffdcb0">30분 이내</mark>에 복구했는지도 기록해 주세요. 마지막으로 담당자가 검토할 규칙 조정(튜닝, tuning: 같은 오탐이 반복되지 않도록 탐지 규칙이나 허용 목록을 고치는 일) 제안을 남겨 주세요.
> - **바뀌는 점**: 두 신고가 <mark style="background:#bde3ff">25분 · 5분</mark> 만에 복구됩니다. 롤백한 뒤에도 잠겨 있거나 차단된 대상은 <mark style="background:#bde3ff">0개</mark>입니다. <mark style="background:#ffc4d6">`jiwoo` 의 세션은 되돌릴 수 없는 조치(비가역, irreversible)라 「되돌리기 불가」로 따로 남습니다.</mark> 그래서 `jiwoo` 가 다시 로그인해야 합니다. `dami` 는 그대로 잠겨 있습니다. 상황과 이름은 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다.

### 📖 4.1 오탐 대응은 「영향 확인 → 롤백 → 복구 확인 → 규칙 조정 제안(튜닝)」 순서로 진행한다

| 순서 | 하는 일 | 오늘 쓰는 함수 |
|---|---|---|
| 1. 영향 확인 | 그 인시던트의 기록 가운데 조치 전(`before`)과 조치 후(`after`)가 다른 기록만 찾는다 | `list_changes` (1 · 2번) |
| 2. 되돌리기 | 자동 조치가 바꾼 것만 조치 이전 상태로 롤백한다 | <mark style="background:#e0d4ff">수요일의 `rollback_incident`</mark> (7번) |
| 3. 복구 확인 | 롤백한 뒤에도 잠겨 있는 계정 · 차단된 IP 가 남았는지 점검한다 | `find_not_recovered` (3 · 4번) |
| 4. 규칙 조정 제안 | IP 차단이었으면 허용 목록 추가 검토, 계정이었으면 탐지 규칙 예외(exception) 검토를 담당자에게 제안한다 | `make_tuning_note` (5 · 6번) |

- <mark style="background:#e0d4ff">4과목 금요일에는 탐지 규칙을 고쳐(튜닝) 오탐 알림을 줄였습니다.</mark> 오늘은 오탐 때문에 **이미 실행된 자동 조치**를 원래 상태로 복원(롤백)하는 일입니다.
- `INC-301` 에는 IP `198.51.100.120` 의 차단 기록도 있지만 `before` 와 `after` 가 모두 <mark style="background:#bde3ff">「변경 없음」</mark>입니다. 바뀐 것이 없으므로 영향 확인 대상에서 제외합니다.
- `rollback_incident` 는 신고된 인시던트의 기록만 롤백합니다. 같은 기록 파일에 있는 `INC-201`(`dami`)은 <mark style="background:#ffc4d6">변경하지 않습니다.</mark>
- <mark style="background:#ffc4d6">세션 종료는 되돌릴 수 없는 조치(비가역, irreversible)입니다.</mark> 이미 종료된 세션은 재개할 수 없고, 사용자가 다시 로그인해야 새 세션이 생성되기 때문입니다. 수요일의 `rollback_incident` 가 「되돌리기 불가」 기록을 남기므로, 담당자는 사용자에게 다시 로그인하라고 안내해야 합니다.
- 규칙 조정 제안은 즉시 적용하지 않습니다. 담당자가 IP 의 소유자와 용도, 예외로 둘 사용자를 검토하고 승인한 뒤에 변경합니다.
- <mark style="background:#ffdcb0">30분(`RECOVERY_LIMIT`)</mark>은 이 수업에서 정한 복구 기준 시간입니다. 지금 시각(`NOW` = 45분)에서 신고 접수 시각을 빼서 복구까지 걸린 시간을 구합니다. 예를 들어 `INC-301` 은 신고 접수 시각이 20분이라 <mark style="background:#bde3ff">45 − 20 = 25분</mark>입니다.

함수 네 개와 실행 파일 가운데 직접 쓰는 곳은 **아홉 군데**입니다.

```
false_positive.py   list_changes           : 바뀐 기록이면 (1번) 추가한다 (2번)
                    find_not_recovered     : 아직 잠긴 계정 (3번) · 아직 차단된 IP (4번) 를 찾는다
                    make_tuning_note       : IP 차단이면 (5번) 허용 목록 추가를 제안한다 (6번)
                    handle_false_positive  : 영향 확인 → 되돌리기 (7번) → 복구 확인 → 제안 순서로 처리한다
실행 파일           day05_4-1_run.py       : 신고마다 처리하고 (8번) 결과를 모은다 (9번)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 4-1 · 오탐(false positive) 신고 2건을 영향 확인 · 롤백 · 복구 확인 · 규칙 조정 제안까지 처리하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>롤백 함수는 있지만, 무엇이 바뀌었는지 확인하고(영향 확인), 실제로 복원됐는지 점검하고(복구 확인), 같은 오탐의 재발을 막을 규칙 조정을 제안하는 절차가 없습니다</mark>.
- **만드는 것**: 영향 확인 · 복구 확인 · 규칙 조정 제안 · 신고 한 건 처리(`false_positive.py`), 신고마다 처리하고 저장하기(`day05_4-1_run.py`).
- **실행하면**: <mark>단계 1: 신고 수와 처리 전 상태, 단계 2: 신고마다 영향 확인 · 되돌리기 · 복구 확인 · 규칙 조정 제안, 단계 3: 처리 뒤 상태, 단계 4: 저장한 파일이 나옵니다.</mark>

**🎯 할 일**: 데이터 파일 세 개와 코드 파일 두 개를 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행해서 단계 2 · 3 을 읽습니다.

**`fp_state.json`** — 오탐을 처리하기 전 연습용 시스템 상태입니다. 수요일의 `containment_state.json` 과 같은 꼴입니다. `junho` 는 오늘 수업 전부터 잠겨 있던 계정입니다. 연습용 시스템(실제 서버를 대신하는 시스템)의 시계(`clock`)는 0 에서 움직이지 않고, 끝난 차단을 해제하는 수요일 함수 `expire_blocks` 도 호출하지 않습니다. 그래서 `block_expiry`(차단이 끝나는 시각)가 있어도 차단이 자동으로 풀리지 않습니다.

```
{"locked_users": ["junho", "dami", "jiwoo"], "blocked_ips": ["198.51.100.90"], "block_expiry": {"198.51.100.90": 120}, "clock": 0, "sessions": {"dami": [], "jiwoo": [], "junho": [], "hana": ["S-601"]}}
```

**`fp_log.json`** — 자동 조치 기록 7건입니다. 수요일의 `containment_log.json` 과 같은 꼴입니다.

```
[
  {"action": "계정 잠금", "target": "dami", "incident": "INC-201", "before": "잠기지 않음", "after": "잠김", "reason": "퇴사한 계정의 서버 요청"},
  {"action": "세션 종료", "target": "dami", "incident": "INC-201", "before": "세션 2개", "after": "세션 0개", "reason": "퇴사한 계정의 서버 요청"},
  {"action": "IP 차단", "target": "198.51.100.90", "incident": "INC-202", "before": "차단되지 않음", "after": "차단됨", "reason": "경로 스캔 (120분 뒤 자동 해제)"},
  {"action": "계정 잠금", "target": "jiwoo", "incident": "INC-301", "before": "잠기지 않음", "after": "잠김", "reason": "해외 IP 에서 로그인"},
  {"action": "세션 종료", "target": "jiwoo", "incident": "INC-301", "before": "세션 1개", "after": "세션 0개", "reason": "해외 IP 에서 로그인"},
  {"action": "IP 차단", "target": "198.51.100.120", "incident": "INC-301", "before": "변경 없음", "after": "변경 없음", "reason": "여러 계정이 함께 쓰는 IP 라서 담당자 승인 필요"},
  {"action": "계정 잠금", "target": "dami", "incident": "INC-205", "before": "잠김", "after": "잠김", "reason": "이미 잠겨 있어 변경 없음"}
]
```

**`fp_reports.json`** — 오탐 신고 2건입니다. `reported_at` 은 신고를 받은 시각(분)입니다.

```
[
  {"incident": "INC-301", "reported_at": 20, "reporter": "영업팀장", "reason": "jiwoo 는 출장 중이고 출장 등록이 되어 있다"},
  {"incident": "INC-202", "reported_at": 40, "reporter": "인프라팀", "reason": "198.51.100.90 은 회사가 계약한 점검 업체의 스캐너 IP 다"}
]
```

**`false_positive.py`** — 오탐 처리 함수 모음입니다. 6교시도 가져와 사용(import)합니다. 수요일의 `rollback.py` 가 같은 폴더에 있어야 합니다. 직접 쓰는 곳은 1 ~ 7번입니다.

- 3번과 4번은 `if` 한 줄만 씁니다. 그 아래 미리 채운 `remaining.append(target)` 줄이 `if` 안쪽입니다.

```python
from rollback import find_incident_records, rollback_incident                        # 수요일에 만든 되돌리기 함수를 불러온다

RECOVERY_LIMIT = 30                                                                  # 오탐 신고를 받은 뒤 복구를 끝내야 하는 시간(분)


def list_changes(log, incident_id):                                                  # 조치 기록 리스트와 인시던트 번호를 받는 함수
    """그 인시던트의 기록 가운데 조치 전과 조치 후가 다른 기록(자동 조치가 실제로 바꾼 것)만 리스트로 리턴한다.
    오탐 신고를 받았을 때, 무엇이 바뀌어서 누가 영향을 받았는지 먼저 확인할 때 쓴다.
    """
    changes = []                                                                     # 실제로 바뀐 기록을 모을 빈 리스트 — 미리 채운 줄
    for record in find_incident_records(log, incident_id):                           # 그 인시던트의 기록을 하나씩 읽는다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 1. record["before"] 와 record["after"] 가 다르면 (if, !=)
            # 2. changes 에 record 를 추가한다 (append)
    return changes                                                                   # 실제로 바뀐 기록 리스트를 리턴한다 — 미리 채운 줄


def find_not_recovered(changes, state):                                              # 바뀐 기록 리스트와 연습용 시스템 상태를 받는 함수
    """되돌린 뒤에도 아직 잠겨 있는 계정이나 차단된 IP 를 리스트로 리턴한다. 빈 리스트이면 복구가 끝난 것이다.
    되돌리기 함수를 실행한 뒤, 실제 상태가 원래대로 돌아왔는지 확인할 때 쓴다.
    """
    remaining = []                                                                   # 아직 복구되지 않은 대상을 모을 빈 리스트 — 미리 채운 줄
    for record in changes:                                                           # 바뀐 기록을 하나씩 읽는다 — 미리 채운 줄
        target = record["target"]                                                    # 조치 대상(계정 또는 IP) — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. record["action"] 이 "계정 잠금" 이고(and) target 이 state["locked_users"] 안에 있으면 (if, ==, in)
            remaining.append(target)                                                 # 아직 잠겨 있는 계정을 추가한다 — 미리 채운 줄
        # 4. record["action"] 이 "IP 차단" 이고(and) target 이 state["blocked_ips"] 안에 있으면 (if, ==, in)
            remaining.append(target)                                                 # 아직 차단된 IP 를 추가한다 — 미리 채운 줄
    return remaining                                                                 # 복구되지 않은 대상 리스트를 리턴한다 — 미리 채운 줄


def make_tuning_note(changes):                                                       # 바뀐 기록 리스트를 받는 함수
    """같은 오탐이 다시 나지 않도록 규칙을 어떻게 고칠지 제안 문장을 만들어 리턴한다.
    복구한 뒤, 탐지 규칙이나 허용 목록을 고치자고 담당자에게 남길 때 쓴다.
    """
    for record in changes:                                                           # 바뀐 기록을 하나씩 읽는다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. record["action"] 이 "IP 차단" 이면 (if, ==)
            # 6. "허용 목록에 추가 검토: " + record["target"] 을 리턴한다
    first = changes[0]                                                               # 첫 번째 바뀐 기록 — 미리 채운 줄
    return "탐지 규칙 예외 검토: " + first["target"] + " (" + first["reason"] + ")"  # 계정이면 규칙 예외를 제안한다 — 미리 채운 줄


def handle_false_positive(report, log, state, now):                                  # 오탐 신고 한 건 · 조치 기록 · 상태 · 지금 시각(분)을 받는 함수
    """오탐 신고 한 건을 영향 확인 → 되돌리기 → 복구 확인 순서로 처리하고, 규칙 조정 제안을 함께 담은 결과 딕셔너리를 리턴한다.
    오탐으로 잘못 잠그거나 차단한 것을 빠르고 빠짐없이 원래대로 돌릴 때 쓴다.
    """
    incident_id = report["incident"]                                                 # 오탐으로 신고된 인시던트 번호 — 미리 채운 줄
    changes = list_changes(log, incident_id)                                         # 영향 확인: 자동 조치가 실제로 바꾼 기록 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. rollback_incident(incident_id, log, state) 의 결과를 undo_records 에 저장한다 (되돌리기)
    remaining = find_not_recovered(changes, state)                                   # 복구 확인: 아직 남은 대상 — 미리 채운 줄
    changed = []                                                                     # 영향 받은 대상과 조치를 모을 빈 리스트 — 미리 채운 줄
    for record in changes:                                                           # 바뀐 기록을 하나씩 읽는다 — 미리 채운 줄
        changed.append(record["action"] + " " + record["target"])                    # 「조치 대상」 꼴로 추가한다 — 미리 채운 줄
    undone = []                                                                      # 되돌린 일을 모을 빈 리스트 — 미리 채운 줄
    for record in undo_records:                                                      # 되돌리기 기록을 하나씩 읽는다 — 미리 채운 줄
        undone.append(record["action"] + " " + record["target"])                     # 「조치 대상」 꼴로 추가한다 — 미리 채운 줄
    minutes = now - report["reported_at"]                                            # 신고를 받은 뒤 걸린 시간(분) — 미리 채운 줄
    result = {                                                                       # 처리 결과 한 건 — 미리 채운 줄
        "incident": incident_id,                                                     # 인시던트 번호
        "changed": changed,                                                          # 영향 받은 대상과 조치
        "undone": undone,                                                            # 되돌린 일
        "remaining": remaining,                                                      # 아직 복구되지 않은 대상
        "minutes": minutes,                                                          # 걸린 시간(분)
        "in_time": minutes <= RECOVERY_LIMIT,                                        # 정한 시간 안에 끝났는지
        "tuning": make_tuning_note(changes),                                         # 규칙 조정 제안
    }
    return result                                                                    # 처리 결과를 리턴한다 — 미리 채운 줄
```

**`day05_4-1_run.py`** — 8 · 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다.

```python
from incident import load_json, save_json                                                   # 월요일 파일의 JSON 읽기 · 쓰기 함수를 불러온다
from false_positive import handle_false_positive, RECOVERY_LIMIT                            # 방금 만든 오탐 처리 함수를 불러온다

NOW = 45                                                                                    # 오탐 신고를 처리하는 지금 시각(분)

state = load_json("fp_state.json")                                                          # 오탐 처리 전 연습용 시스템 상태를 읽는다
log = load_json("fp_log.json")                                                              # 자동 조치 기록을 리스트로 읽는다
reports = load_json("fp_reports.json")                                                      # 오탐 신고 파일을 리스트로 읽는다
print("--- 단계 1: 오탐 신고", len(reports), "건 · 조치 기록", len(log), "건 · 지금", NOW, "분")  # 단계 1 시작을 알리는 줄
print("처리 전 잠긴 계정:", state["locked_users"], "· 차단된 IP:", state["blocked_ips"])    # 처리 전 상태를 출력한다

results = []                                                                                # 신고마다 처리 결과를 저장할 빈 리스트
print("--- 단계 2: 신고마다 영향 확인 · 되돌리기 · 복구 확인 · 규칙 조정 제안")             # 단계 2 시작을 알리는 줄
for report in reports:                                                                      # 오탐 신고를 하나씩 읽는다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 8. handle_false_positive(report, log, state, NOW) 의 결과를 result 에 저장한다
    # 9. results 에 result 를 추가한다 (append)
    print("[" + result["incident"] + "] 신고:", report["reporter"], "—", report["reason"])  # 신고 내용을 출력한다
    print(" - 영향 확인:", result["changed"])                                               # 자동 조치가 바꾼 것을 출력한다
    print(" - 되돌리기:", result["undone"])                                                 # 되돌린 일을 출력한다
    print(" - 복구 확인: 아직 잠기거나 차단된 대상", result["remaining"], "· 걸린 시간", result["minutes"], "분 · 기준", RECOVERY_LIMIT, "분 안", result["in_time"])  # 복구 확인 결과를 출력한다
    print(" - 규칙 조정 제안:", result["tuning"])                                           # 규칙 조정 제안을 출력한다

print("--- 단계 3: 처리 뒤 상태 (오탐이 아닌 계정은 그대로인지)")                           # 단계 3 시작을 알리는 줄
print("잠긴 계정:", state["locked_users"], "· 차단된 IP:", state["blocked_ips"])            # 처리 뒤 상태를 출력한다
print("dami 는 아직 잠김:", "dami" in state["locked_users"])                                # 진짜 공격(퇴사한 계정)은 그대로 잠겨 있는지 출력한다

save_json(results, "fp_results.json")                                                       # 처리 결과를 파일에 저장한다
save_json(state, "fp_state_after.json")                                                     # 처리 뒤 상태를 다른 파일에 저장한다
print("--- 단계 4: fp_results.json 에", len(results), "건 · fp_state_after.json 저장 · 기준", RECOVERY_LIMIT, "분")  # 단계 4 시작을 알리는 줄
```

**순서**

1. **[터미널]** 파일 다섯 개를 만들고 **[VS Code]** 에서 열어 붙여 넣습니다.
   ```bash
   pwd
   touch fp_state.json fp_log.json fp_reports.json false_positive.py day05_4-1_run.py
   ls
   ```
2. **[VS Code]** `false_positive.py` 1 ~ 7번, `day05_4-1_run.py` 8 · 9번을 씁니다. 막히면 아래 「4교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 가 `soar_response` 로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   python day05_4-1_run.py
   ```
4. 출력은 네 단계입니다. 제목 줄은 줄 수에 넣지 않습니다.
   - 단계 1 은 숫자가 제목 줄에 함께 나오고 그 아래 1줄입니다.
   - 단계 2 는 10줄(신고 한 건에 5줄씩), 단계 3 은 2줄입니다.
   - 단계 4 는 숫자가 제목 줄에 함께 나와 그 아래 줄이 없습니다.
5. **[보고서]** `day05_am_report.md` 의 `## 4교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 신고마다 걸린 시간과 처리 뒤 잠긴 계정을 적어 주세요.
   - (나) 🔍 `INC-301` 의 영향 확인에 `IP 차단 198.51.100.120` 이 없습니다. `fp_log.json` 에서 `198.51.100.120` 의 IP 차단 기록이 가진 `before` · `after` 를 근거로 그 이유를 적고, `false_positive.py` 1번의 `if` 줄이 없으면 규칙 조정 제안이 어떻게 잘못되는지 적어 주세요.
   - (다) 🔍 `INC-301` 의 되돌리기에 `되돌리기 불가 jiwoo` 가 있습니다. 무엇을 되돌릴 수 없는지(비가역 조치)와 담당자가 `jiwoo` 에게 따로 안내해야 할 것을 적어 주세요. 그리고 `dami` 가 처리 뒤에도 잠겨 있어야 하는 이유를 따로 적어 주세요.

### 4교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 두 값이 다르면 | `if record["before"] != record["after"]:` |
| 리스트에 추가 | `changes.append(record)` |
| 두 조건을 함께 | `if record["action"] == "계정 잠금" and target in state["locked_users"]:` |
| 같으면 | `if record["action"] == "IP 차단":` |
| 문자열을 이어 붙여 리턴 | `return "허용 목록에 추가 검토: " + record["target"]` |
| 함수 결과를 변수에 저장하기 | `undo_records = rollback_incident(incident_id, log, state)` |

---

## 오늘 오전 마무리

| 확인 | 문제 |
|---|---|
| 티켓과 조치 기록을 대조해 리포트 파일을 생성하고, 티켓이 없는 조치까지 찾았다 | 오전 2-1 |
| 조치 요청을 위험 점수로 자동 · 승인 필요 · 차단 금지로 분류했다 | 오전 3-1 |
| 오탐 신고를 영향 확인 · 롤백 · 복구 확인 · 규칙 조정 제안까지 처리했다 | 오전 4-1 |

<mark>오후 5교시에는 자동 조치마다 운영 위험을 평가한 문서(`risk_assessment.md`)를 새로 작성합니다. 6교시에는 오전의 `report.py` · `approval_gate.py` · `false_positive.py` 를 가져와 사용(import)해 오늘 만든 것을 한 번에 점검합니다.</mark>

---

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

아래 답은 한 예이고, <mark>핵심이 같으면 맞습니다.</mark> 줄 수가 달라도 주석이 말한 일을 하면 맞습니다.

---

### 정답 2-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day05_2-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예)

`report.py` 의 1 ~ 8번입니다.

```python
    # 1. table["acked_at"] - table["created_at"] 를 table["ack_minutes"] 에 저장한다 (확인까지 걸린 분)
    table["ack_minutes"] = table["acked_at"] - table["created_at"]  # 두 열을 빼서 확인까지 걸린 분 열을 만든다
    # 2. table["rule"].value_counts() 를 rule_counts 에 저장한다
    rule_counts = table["rule"].value_counts()                      # 규칙 열에서 값마다 개수를 센다
    # 3. table["acked_at"] >= 0 인 행만 남겨 acked 에 저장한다 (확인한 티켓만)
    acked = table[table["acked_at"] >= 0]                           # 확인한 티켓(acked_at 이 0 이상)만 남긴다
    # 4. groups["ack_minutes"].mean() 을 grade_means 에 저장한다 (등급마다 평균)
    grade_means = groups["ack_minutes"].mean()                      # 등급마다 확인까지 걸린 분의 평균을 구한다
    # 5. table["acked_at"] > table["sla_due"] 인 행만 남겨 late 에 저장한다
    late = table[table["acked_at"] > table["sla_due"]]              # 응답 기한 시각보다 늦게 확인한 행만 남긴다
        # 6. action["incident"] 가 covered 안에 없으면 (if, not in)
        if action["incident"] not in covered:                       # 티켓에 없는 인시던트이면
            # 7. missing 에 action 을 추가한다 (append)
            missing.append(action)                                  # 그 조치 기록을 추가한다
        # 8. "- " + rule + ": " + str(count) + "장" 을 lines 에 추가한다 (append)
        lines.append("- " + rule + ": " + str(count) + "장")        # 규칙 한 줄을 추가한다
```

`day05_2-1_run.py` 의 9번입니다.

```python
# 9. make_ticket_table(tickets) 의 결과를 table 에 저장한다
table = make_ticket_table(tickets)  # 티켓 리스트를 표로 바꾸고 확인까지 걸린 분 열을 더한다
```

**결과**

- (가) 출력은 다음과 같습니다. 티켓이 가장 많은 규칙은 <mark style="background:#bde3ff">**퇴사한 계정 · 경로 스캔**</mark>(각 2장)이고, 리포트 파일은 <mark style="background:#bde3ff">**32줄**</mark>입니다.

```
--- 단계 1: 불러온 티켓 7 장 · 조치 기록 10 건
--- 단계 2: 규칙별 티켓 수
퇴사한 계정 : 2 장
경로 스캔 : 2 장
규칙은 허용인데 서버가 거절 : 1 장
대량 다운로드 : 1 장
업무 시간 밖 로그인 : 1 장
--- 단계 3: 등급별 평균 확인 시간(분)
high : 10.0 분
mid : 85.0 분
--- 단계 4: 응답 기한을 넘겨 확인한 티켓 2 장 · 티켓이 없는 조치 1 건
TCK-3 기한 68 분 · 확인 80 분
TCK-4 기한 72 분 · 확인 140 분
INC-212 계정 잠금 yuna → 티켓 없음
--- 단계 5: 리포트 파일 incident_report_20261112.md · 32 줄 저장
```

리포트 파일 `incident_report_20261112.md` 의 내용은 다음과 같습니다.

```
# 초동 대응 리포트 — 2026-11-12(목) 오전 근무

## 1. 티켓별 초동 대응
- TCK-1 [high] dami — 퇴사한 계정 · 상태 해결 · 조치 기록 4건
- TCK-2 [low] 198.51.100.90 — 경로 스캔 · 상태 열림 · 조치 기록 2건
- TCK-3 [mid] gaeun — 규칙은 허용인데 서버가 거절 · 상태 해결 · 조치 기록 0건
- TCK-4 [mid] seoyeon — 대량 다운로드 · 상태 확인 중 · 조치 기록 0건
- TCK-5 [low] 203.0.113.250 — 경로 스캔 · 상태 열림 · 조치 기록 1건
- TCK-6 [mid] hana — 업무 시간 밖 로그인 · 상태 해결 · 조치 기록 0건
- TCK-7 [high] dami — 퇴사한 계정 · 상태 확인 중 · 조치 기록 2건

## 2. 규칙별 티켓 수
- 퇴사한 계정: 2장
- 경로 스캔: 2장
- 규칙은 허용인데 서버가 거절: 1장
- 대량 다운로드: 1장
- 업무 시간 밖 로그인: 1장

## 3. 등급별 평균 확인 시간(분)
- high: 10.0분
- mid: 85.0분

## 4. 응답 기한을 넘겨 확인한 티켓
- TCK-3 · 기한 68분 · 확인 80분
- TCK-4 · 기한 72분 · 확인 140분

## 5. 티켓이 없는 조치 (사람이 티켓을 만들어야 함)
- INC-212 · 계정 잠금 · yuna

## 6. 높음(high) 티켓의 처리 경위
- TCK-1 · dami: 0분 티켓 생성 → 10분 담당자 확인 → 45분 해결
- TCK-7 · dami: 95분 티켓 생성 → 105분 담당자 확인
```

- (나) `TCK-2` 와 `TCK-5` 는 `acked_at` 이 <mark style="background:#bde3ff">`-1`</mark>(아직 확인하지 않음)입니다. 3번에서 `acked_at` 이 0 이상인 행만 필터링하므로 low 티켓이 하나도 남지 않아, 단계 3 의 평균 확인 시간 집계에 low 가 나오지 않습니다.
  - 3번에서 확인한 티켓만 필터링하지 않으면 low 의 평균이 ((−1 − 3) + (−1 − 30)) ÷ 2 = <mark style="background:#ffc4d6">**−17.5분**</mark>으로 나옵니다. 확인하지 않은 티켓을 「빨리 확인했다」고 잘못 보고하게 되고, 평균 확인 시간 지표가 실제와 다르게 왜곡됩니다.
- (다) `covered` 에는 티켓 7장에 병합된 인시던트 번호(`INC-201` ~ `INC-211`)만 들어 있습니다. `INC-212` 는 어느 티켓에도 없어서 `not in covered` 가 참이 되므로 `missing` 에 추가됩니다(추적 누락 탐지).
  - <mark style="background:#ffc4d6">이 절이 없으면 `yuna` 계정을 잠근 조치가 리포트에서 누락됩니다.</mark> 고객사는 `yuna` 가 왜 로그인하지 못하는지 알 수 없고, 담당자도 이 사건을 확인하지 않습니다.

**왜**

- <mark>리포트에 「티켓에 적힌 것」만 옮기면 누락되는 사건이 생깁니다.</mark> 조치 기록과 티켓을 대조(reconciliation)해 티켓이 없는 조치를 따로 적으면, 조치는 실행됐는데 리포트에 없는 사건을 찾을 수 있습니다.

**자주 틀리는 곳**

아래 결과는 해당 번호의 줄을 지우고 실행한 것입니다.

- 1번을 비워 두면 `ack_minutes` 열이 없어서 4번에서 오류가 납니다. <mark style="background:#ffc4d6">**열을 만든 뒤에 그 열로 평균을 구해야 합니다.**</mark>

```
KeyError: 'Column not found: ack_minutes'
```

- 2번을 비워 두면 `rule_counts` 가 만들어지지 않아 오류가 납니다. 3 · 4 · 5번을 비워도 같은 꼴의 오류(`name 'acked'` · `name 'grade_means'` · `name 'late'`)가 납니다. 파이썬 버전에 따라 뒤에 `Did you mean: …` 이 더 붙을 수 있습니다.

```
NameError: name 'rule_counts' is not defined
```

- 3번에서 확인한 티켓만 남기지 않고 `acked = table` 로 쓰면 오류 없이 <mark style="background:#ffc4d6">**low 의 평균이 음수로 나옵니다.**</mark> 단계 3 의 `low : -17.5 분` 줄이 이 실수의 결과입니다.

```
--- 단계 3: 등급별 평균 확인 시간(분)
high : 10.0 분
low : -17.5 분
mid : 85.0 분
```

- 6번을 비워 두면 7번 줄이 `for` 바로 아래 줄이 되어 오류 없이 <mark style="background:#ffc4d6">**모든 조치 기록이 「티켓 없음」으로 나옵니다.**</mark> 단계 4 의 제목 줄이 1건이 아니라 10건으로 나오는 것이 이 실수의 결과입니다.

```
--- 단계 4: 응답 기한을 넘겨 확인한 티켓 2 장 · 티켓이 없는 조치 10 건
```

- 7번을 비워 두면 `if` 아래에 실행할 줄이 없어 실행하기 전에 멈춥니다. `IndentationError`(들여쓰기 오류: 줄 앞의 빈칸이 맞지 않다는 뜻)로 시작하는 오류입니다(문구는 파이썬 버전마다 조금 다릅니다).

```
IndentationError: expected an indented block
```

- 8번을 비워 두면 오류 없이 <mark style="background:#ffc4d6">**리포트 2절이 제목만 남고 비어 있습니다.**</mark> 단계 5 의 줄 수가 32줄이 아니라 27줄로 나오는 것이 이 실수의 결과입니다.

```
--- 단계 5: 리포트 파일 incident_report_20261112.md · 27 줄 저장
```

- 9번을 비워 두면 `table` 이 만들어지지 않아 오류가 납니다. 파이썬 버전에 따라 뒤에 `Did you mean: …` 이 더 붙을 수 있습니다.

```
NameError: name 'table' is not defined
```

**관제에서는**

- 초동 대응 리포트는 사건 직후 정리해 전달하는 보고라서, 정해진 양식(템플릿, template)에 맞춰 자동으로 작성하는 제품도 있습니다. 보고에는 평균 확인 시간 · 평균 해결 시간 같은 지표를 함께 싣는 경우가 많습니다. <mark>전달하기 전에 「조치는 했는데 티켓이 없는 것」처럼 누락된 데이터를 먼저 점검합니다.</mark> 오늘의 절 다섯 개는 예시이고, 실제 양식은 고객사와 정한 대로 작성합니다.

---

### 정답 3-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day05_3-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예)

`approval_gate.py` 의 1 ~ 7번입니다.

```python
    # 1. request["target"] 이 policy["allowlist_ips"] 안에 있는지(in)의 결과를 리턴한다
    return request["target"] in policy["allowlist_ips"]  # 대상이 허용 목록에 있는지의 결과를 리턴한다
    # 2. grade_table[request["grade"]] 를 score 에 저장한다 (등급 점수로 시작한다)
    score = grade_table[request["grade"]]                # 이 요청 등급의 점수로 시작한다
    # 3. request["target"] 이 policy["vip_accounts"] 안에 있으면 (if, in)
    if request["target"] in policy["vip_accounts"]:      # 대상이 VIP 계정이면
        # 4. score 에 score + policy["vip_points"] 를 저장한다 (VIP 점수를 더한다)
        score = score + policy["vip_points"]             # VIP 점수를 더한다
    # 5. is_allowlisted(request, policy) 가 참이면 (if)
    if is_allowlisted(request, policy):                  # 허용 목록 대상이면
    # 6. risk_score(request, policy) 의 두 결과를 score, reasons 에 저장한다
    score, reasons = risk_score(request, policy)         # 위험 점수와 이유 리스트를 함께 받는다
    # 7. score 가 policy["approval_score"] 이상이면 (if, >=)
    if score >= policy["approval_score"]:                # 승인 기준 점수 이상이면
```

위 줄만으로는 `if` 안에 들어가는 줄이 어느 것인지 알기 어려우니, 미리 채운 줄까지 넣은 두 함수의 완성된 모양을 함께 봅니다.

**전체 모양 — `risk_score`**

```python
def risk_score(request, policy):                                            # 조치 요청 한 건과 승인 정책을 받는 함수
    """등급 · VIP · 함께 쓰는 IP · 대상 수로 위험 점수를 더하고, 점수와 이유 리스트를 함께 리턴한다.
    자동으로 실행해도 되는 요청인지 숫자로 판단할 때 쓴다.
    """
    grade_table = policy["grade_points"]                                    # 등급마다 정한 점수 표 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    score = grade_table[request["grade"]]                                   # 이 요청 등급의 점수로 시작한다
    reasons = ["등급 " + request["grade"] + " +" + str(score)]              # 점수를 더한 이유 리스트 — 미리 채운 줄
    if request["target"] in policy["vip_accounts"]:                         # 대상이 VIP 계정이면
        score = score + policy["vip_points"]                                # VIP 점수를 더한다
        reasons.append("VIP 계정 +" + str(policy["vip_points"]))            # 이유를 추가한다 — 미리 채운 줄
    if request["users_on_ip"] >= policy["shared_ip_limit"]:                 # 여러 계정이 함께 쓰는 IP 이면 — 미리 채운 줄
        score = score + policy["shared_ip_points"]                          # 함께 쓰는 IP 점수를 더한다 — 미리 채운 줄
        reasons.append("함께 쓰는 IP +" + str(policy["shared_ip_points"]))  # 이유를 추가한다 — 미리 채운 줄
    if request["target_count"] > policy["many_targets_limit"]:              # 한 번에 조치할 대상이 많으면 — 미리 채운 줄
        score = score + policy["many_targets_points"]                       # 대상 수 점수를 더한다 — 미리 채운 줄
        reasons.append("대상 " + str(request["target_count"]) + "개 +" + str(policy["many_targets_points"]))  # 이유를 추가한다 — 미리 채운 줄
    return score, reasons                                                   # 점수와 이유 리스트를 함께 리턴한다 — 미리 채운 줄
```

**전체 모양 — `decide_gate`**

```python
def decide_gate(request, policy):                 # 조치 요청 한 건과 승인 정책을 받는 함수
    """조치 요청 한 건을 「차단 금지」 · 「승인 필요」 · 「자동」 가운데 하나로 정하고, 결정과 이유 리스트를 함께 리턴한다.
    자동 대응이 조치를 실행하기 직전에, 사람의 승인이 필요한지 정할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    if is_allowlisted(request, policy):           # 허용 목록 대상이면
        return "차단 금지", ["허용 목록 대상"]    # 결정과 이유를 함께 리턴한다 — 미리 채운 줄
    score, reasons = risk_score(request, policy)  # 위험 점수와 이유 리스트를 함께 받는다
    reasons.append("합계 " + str(score) + "점")   # 합계 점수를 이유에 추가한다 — 미리 채운 줄
    if score >= policy["approval_score"]:         # 승인 기준 점수 이상이면
        return "승인 필요", reasons               # 결정과 이유를 함께 리턴한다 — 미리 채운 줄
    return "자동", reasons                        # 기준보다 낮으면 자동으로 실행한다 — 미리 채운 줄
```

`day05_3-1_run.py` 의 8 · 9번입니다.

```python
    # 8. decide_gate(request, policy) 의 두 결과를 decision, reasons 에 저장한다
    decision, reasons = decide_gate(request, policy)  # 결정과 이유 리스트를 함께 받는다
    # 9. counts[decision] 에 counts[decision] + 1 을 저장한다 (1 늘린다)
    counts[decision] = counts[decision] + 1           # 이 결정의 요청 수를 1 늘린다
```

**결과**

- (가) 출력은 다음과 같습니다. 자동 <mark style="background:#bde3ff">**3건**</mark> · 승인 필요 <mark style="background:#bde3ff">**3건**</mark> · 차단 금지 <mark style="background:#bde3ff">**2건**</mark>이고, 승인 필요는 `REQ-2` · `REQ-5` · `REQ-6` 입니다.

```
--- 단계 1: 불러온 조치 요청 8 건 · 승인 기준 3 점
--- 단계 2: 요청마다 결정과 이유
REQ-1 계정 잠금 dami → 자동 · 등급 high +2, 합계 2점
REQ-2 계정 잠금 gaeun → 승인 필요 · 등급 mid +1, VIP 계정 +3, 합계 4점
REQ-3 IP 차단 203.0.113.80 → 차단 금지 · 허용 목록 대상
REQ-4 IP 차단 198.51.100.45 → 자동 · 등급 low +0, 합계 0점
REQ-5 IP 차단 198.51.100.77 → 승인 필요 · 등급 mid +1, 함께 쓰는 IP +2, 합계 3점
REQ-6 계정 잠금 minsu → 승인 필요 · 등급 high +2, 대상 6개 +2, 합계 4점
REQ-7 세션 종료 hana → 자동 · 등급 mid +1, 합계 1점
REQ-8 IP 차단 192.0.2.10 → 차단 금지 · 허용 목록 대상
--- 단계 3: 결정별 요청 수
자동 : 3 건
승인 필요 : 3 건
차단 금지 : 2 건
--- 단계 4: 담당자에게 보낼 승인 요청
REQ-2 INC-312 계정 잠금 gaeun → 담당자 승인을 기다림
REQ-5 INC-315 IP 차단 198.51.100.77 → 담당자 승인을 기다림
REQ-6 INC-316 계정 잠금 minsu → 담당자 승인을 기다림
--- 단계 5: gate_results.json 에 8 건 저장
```

- (나) `REQ-1` 은 등급 high 2점뿐이라 <mark style="background:#bde3ff">합계 2점</mark>으로 <mark style="background:#ffdcb0">임계값(3점)</mark>보다 낮아 자동입니다. `REQ-6` 은 등급 2점에 대상 6개 2점을 더해 <mark style="background:#bde3ff">합계 4점</mark>이라 승인 필요입니다.
  - 대상이 많으면 잘못 실행했을 때 여러 사용자의 계정이 한꺼번에 잠기므로, 영향 범위가 넓은 조치입니다. <mark style="background:#e0d4ff">화요일의 인사 시스템 오류(퇴사자 알림이 한꺼번에 많이 들어온 일)</mark>처럼 입력이 잘못되면 대상 수가 갑자기 늘 수 있습니다.
- (다) 허용 목록 대상은 차단하면 업무가 중단되는 대상이라, <mark>점수와 무관하게 차단하지 않아야 합니다.</mark> 점수부터 판단하면 `REQ-3`(4점)처럼 점수가 높은 요청이 「승인 필요」가 되고, 담당자가 실수로 승인하면 협력사 사무실 IP 가 차단됩니다.
  - 기준을 설정 파일로 분리하면 코드를 수정하지 않고 숫자만 바꿔 정책을 조정할 수 있고, 설정 파일을 깃(git)으로 관리하면 누가 언제 기준을 바꿨는지 변경 이력(change history)으로 남습니다.

**왜**

- <mark>승인 게이트는 「먼저 실행하면 안 되는 대상을 제외하고, 그다음 위험이 큰 조치만 사람에게 승인을 요청하는」 순서입니다.</mark> 모든 요청에 승인을 요구하면 요청이 너무 많아져서 담당자가 내용을 자세히 보지 않고 승인하게 됩니다. 반대로 모든 요청을 자동으로 실행하면 큰 실수를 막지 못합니다.

**자주 틀리는 곳**

아래 결과는 해당 번호의 줄을 지우고 실행한 것입니다.

- 1번을 비워 두면 `is_allowlisted` 가 아무것도 리턴하지 않아 <mark style="background:#ffc4d6">**허용 목록 대상도 점수로 정해집니다.**</mark> 점검 서버 `192.0.2.10` 이 「자동」으로 차단되는 것이 이 실수의 결과입니다.

```
REQ-3 IP 차단 203.0.113.80 → 승인 필요 · 등급 high +2, 함께 쓰는 IP +2, 합계 4점
REQ-8 IP 차단 192.0.2.10 → 자동 · 등급 low +0, 합계 0점
```

- 2번을 비워 두면 `score` 를 만들기 전에 쓰게 되어 오류가 납니다. 파이썬 3.11 부터는 같은 오류가 `cannot access local variable 'score' …` 문구로 나옵니다.

```
UnboundLocalError: local variable 'score' referenced before assignment
```

- 3번을 비워 두면 4번 줄이 앞줄보다 안쪽으로 들어가 있어 실행하기 전에 멈춥니다. 5번과 7번을 비워도 같은 오류가 납니다.

```
IndentationError: unexpected indent
```

- 4번을 비워 두면 오류 없이 <mark style="background:#ffc4d6">**이유에는 「VIP 계정 +3」이 있는데 점수에는 더해지지 않습니다.**</mark> `REQ-2` 가 합계 1점으로 「자동」이 되는 것이 이 실수의 결과입니다.

```
REQ-2 계정 잠금 gaeun → 자동 · 등급 mid +1, VIP 계정 +3, 합계 1점
```

- 6번을 비워 두면 `reasons` 가 만들어지지 않아 오류가 납니다.

```
NameError: name 'reasons' is not defined
```

- 7번에서 `>=` 대신 `>` 를 쓰면 오류 없이 <mark style="background:#ffc4d6">**기준과 같은 3점이 「자동」이 됩니다.**</mark> `REQ-5` 가 자동으로 나오는 것이 이 실수의 결과입니다.

```
REQ-5 IP 차단 198.51.100.77 → 자동 · 등급 mid +1, 함께 쓰는 IP +2, 합계 3점
```

- 8번을 비워 두면 `decision` 이 만들어지지 않아 9번 줄에서 오류가 납니다.

```
NameError: name 'decision' is not defined
```

- 9번을 비워 두면 오류 없이 <mark style="background:#ffc4d6">**결정별 요청 수가 모두 0건으로 나옵니다.**</mark>

```
--- 단계 3: 결정별 요청 수
자동 : 0 건
승인 필요 : 0 건
차단 금지 : 0 건
```

**관제에서는**

- SOAR(Security Orchestration, Automation and Response, 쏘아: 보안 오케스트레이션 · 자동화 · 대응) 제품의 플레이북에는 조치 직전에 사람의 승인을 받는 단계(휴먼 인 더 루프)를 넣을 수 있고, 어떤 조치를 승인 없이 실행할지는 팀이 정합니다. 위험이 낮은 조치는 자동으로, 업무에 영향을 줄 수 있는 조치는 분석가의 승인을 받는 방식이 일반적입니다. <mark>점수와 임계값을 설정 파일에 분리해 두면, 운영하면서 오탐 · 사고 기록을 보고 승인 기준을 조정하기 쉽습니다.</mark> 오늘의 점수와 3점 임계값은 예시입니다.

---

### 정답 4-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day05_4-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예)

`false_positive.py` 의 1 ~ 7번입니다.

```python
        # 1. record["before"] 와 record["after"] 가 다르면 (if, !=)
        if record["before"] != record["after"]:                                  # 조치 전과 조치 후가 다르면
            # 2. changes 에 record 를 추가한다 (append)
            changes.append(record)                                               # 실제로 바뀐 기록을 추가한다
        # 3. record["action"] 이 "계정 잠금" 이고(and) target 이 state["locked_users"] 안에 있으면 (if, ==, in)
        if record["action"] == "계정 잠금" and target in state["locked_users"]:  # 잠금 기록인데 아직 잠겨 있으면
        # 4. record["action"] 이 "IP 차단" 이고(and) target 이 state["blocked_ips"] 안에 있으면 (if, ==, in)
        if record["action"] == "IP 차단" and target in state["blocked_ips"]:     # 차단 기록인데 아직 차단되어 있으면
        # 5. record["action"] 이 "IP 차단" 이면 (if, ==)
        if record["action"] == "IP 차단":                                        # IP 차단 기록이면
            # 6. "허용 목록에 추가 검토: " + record["target"] 을 리턴한다
            return "허용 목록에 추가 검토: " + record["target"]                  # 허용 목록에 넣자고 제안한다
    # 7. rollback_incident(incident_id, log, state) 의 결과를 undo_records 에 저장한다 (되돌리기)
    undo_records = rollback_incident(incident_id, log, state)                    # 자동 조치가 바꾼 것만 거꾸로 되돌린다
```

3 · 4번은 `if` 만 쓰고 `if` 안에 들어가는 줄은 미리 채운 줄이니, 완성된 모양을 함께 봅니다.

**전체 모양 — `find_not_recovered`**

```python
def find_not_recovered(changes, state):                                          # 바뀐 기록 리스트와 연습용 시스템 상태를 받는 함수
    """되돌린 뒤에도 아직 잠겨 있는 계정이나 차단된 IP 를 리스트로 리턴한다. 빈 리스트이면 복구가 끝난 것이다.
    되돌리기 함수를 실행한 뒤, 실제 상태가 원래대로 돌아왔는지 확인할 때 쓴다.
    """
    remaining = []                                                               # 아직 복구되지 않은 대상을 모을 빈 리스트 — 미리 채운 줄
    for record in changes:                                                       # 바뀐 기록을 하나씩 읽는다 — 미리 채운 줄
        target = record["target"]                                                # 조치 대상(계정 또는 IP) — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        if record["action"] == "계정 잠금" and target in state["locked_users"]:  # 잠금 기록인데 아직 잠겨 있으면
            remaining.append(target)                                             # 아직 잠겨 있는 계정을 추가한다 — 미리 채운 줄
        if record["action"] == "IP 차단" and target in state["blocked_ips"]:     # 차단 기록인데 아직 차단되어 있으면
            remaining.append(target)                                             # 아직 차단된 IP 를 추가한다 — 미리 채운 줄
    return remaining                                                             # 복구되지 않은 대상 리스트를 리턴한다 — 미리 채운 줄
```

`day05_4-1_run.py` 의 8 · 9번입니다.

```python
    # 8. handle_false_positive(report, log, state, NOW) 의 결과를 result 에 저장한다
    result = handle_false_positive(report, log, state, NOW)  # 신고 한 건을 처리하고 결과를 받는다
    # 9. results 에 result 를 추가한다 (append)
    results.append(result)                                   # 처리 결과를 추가한다
```

**결과**

- (가) 출력은 다음과 같습니다. 걸린 시간은 `INC-301` 이 <mark style="background:#bde3ff">**25분**</mark>, `INC-202` 가 <mark style="background:#bde3ff">**5분**</mark>이고 둘 다 30분 안입니다. 처리 뒤 잠긴 계정은 <mark style="background:#bde3ff">`junho` · `dami`</mark> 입니다.

```
--- 단계 1: 오탐 신고 2 건 · 조치 기록 7 건 · 지금 45 분
처리 전 잠긴 계정: ['junho', 'dami', 'jiwoo'] · 차단된 IP: ['198.51.100.90']
--- 단계 2: 신고마다 영향 확인 · 되돌리기 · 복구 확인 · 규칙 조정 제안
[INC-301] 신고: 영업팀장 — jiwoo 는 출장 중이고 출장 등록이 되어 있다
 - 영향 확인: ['세션 종료 jiwoo', '계정 잠금 jiwoo']
 - 되돌리기: ['되돌리기 불가 jiwoo', '계정 해제 jiwoo']
 - 복구 확인: 아직 잠기거나 차단된 대상 [] · 걸린 시간 25 분 · 기준 30 분 안 True
 - 규칙 조정 제안: 탐지 규칙 예외 검토: jiwoo (해외 IP 에서 로그인)
[INC-202] 신고: 인프라팀 — 198.51.100.90 은 회사가 계약한 점검 업체의 스캐너 IP 다
 - 영향 확인: ['IP 차단 198.51.100.90']
 - 되돌리기: ['IP 해제 198.51.100.90']
 - 복구 확인: 아직 잠기거나 차단된 대상 [] · 걸린 시간 5 분 · 기준 30 분 안 True
 - 규칙 조정 제안: 허용 목록에 추가 검토: 198.51.100.90
--- 단계 3: 처리 뒤 상태 (오탐이 아닌 계정은 그대로인지)
잠긴 계정: ['junho', 'dami'] · 차단된 IP: []
dami 는 아직 잠김: True
--- 단계 4: fp_results.json 에 2 건 · fp_state_after.json 저장 · 기준 30 분
```

- (나) 그 기록은 `before` 와 `after` 가 모두 <mark style="background:#bde3ff">「변경 없음」</mark>입니다. 함께 쓰는 IP 라서 담당자 승인을 기다리느라 차단하지 않았으므로, 자동 조치가 바꾼 것이 없어 영향 확인 대상에서 제외됩니다.
  - 1번의 `if` 가 없으면 이 기록도 영향 확인에 들어가고, 규칙 조정 제안이 「허용 목록에 추가 검토: 198.51.100.120」으로 바뀝니다. 여러 계정이 함께 쓰는 IP(`fp_log.json` 의 사유)를 <mark style="background:#ffc4d6">허용 목록에 넣자는 잘못된 제안</mark>입니다.
- (다) <mark style="background:#ffc4d6">종료한 세션은 되돌릴 수 없는 조치(비가역)입니다.</mark> 담당자는 `jiwoo` 에게 「계정은 해제했으니 다시 로그인하면 된다」고 안내해야 합니다.
  - `dami` 는 퇴사한 계정이라 정탐(true positive)인 진짜 공격(`INC-201`)이고 오탐 신고가 없었습니다. <mark>오탐 처리는 신고된 인시던트만 롤백해야 하므로</mark>, `dami` 는 그대로 잠겨 있어야 합니다.

**왜**

- <mark>오탐 복구는 세 가지를 모두 충족해야 완료됩니다. 정한 시간 안에 복구하고, 바뀐 것을 빠짐없이 롤백하고, 진짜 공격에 한 조치는 그대로 유지합니다.</mark>
- 롤백한 뒤 실제 상태를 다시 점검하고(복구 확인) 규칙 조정 제안까지 남겨야, 같은 오탐 알림이 반복되지 않습니다.

**자주 틀리는 곳**

아래 결과는 해당 번호의 줄을 지우고 실행한 것입니다.

- 1번을 비워 두면 2번 줄이 `for` 바로 아래 줄이 되어 오류 없이 <mark style="background:#ffc4d6">**바뀌지 않은 기록까지 영향 확인에 들어갑니다.**</mark> 아래 두 줄(영향 확인 · 규칙 조정 제안)이 이 실수의 결과입니다.

```
 - 영향 확인: ['IP 차단 198.51.100.120', '세션 종료 jiwoo', '계정 잠금 jiwoo']
 - 규칙 조정 제안: 허용 목록에 추가 검토: 198.51.100.120
```

- 2번을 비워 두면 `if` 아래에 실행할 줄이 없어 실행하기 전에 멈춥니다. 6번을 비워도 같은 오류가 납니다(문구는 파이썬 버전마다 조금 다릅니다).

```
IndentationError: expected an indented block
```

- 3번을 비워 두면 미리 채운 `remaining.append(target)` 줄이 앞줄보다 들여써져 있어 실행하기 전에 멈춥니다.

```
IndentationError: unexpected indent
```

- 3번에서 `and target in state["locked_users"]` 를 빠뜨리면 오류 없이 <mark style="background:#ffc4d6">**이미 해제된 `jiwoo` 가 「아직 잠기거나 차단된 대상」으로 나옵니다.**</mark> 잠금 기록이 있다는 것만 보고 지금 상태를 보지 않았기 때문입니다.

```
 - 복구 확인: 아직 잠기거나 차단된 대상 ['jiwoo'] · 걸린 시간 25 분 · 기준 30 분 안 True
```

- 4번을 비워 두면 오류는 나지 않고 출력도 정답과 같습니다. 아래 `remaining.append(target)` 줄이 3번 `if` 안으로 들어가서, <mark style="background:#ffc4d6">**IP 차단이 풀리지 않아도 찾지 못합니다.**</mark> 오늘 샘플은 IP 차단이 모두 풀려서 4번을 비워도 출력이 같으니, 출력이 맞아도 코드를 다시 읽어 확인합니다.
- 5번을 비워 두면 6번 줄이 `for` 바로 아래 줄이 되어 오류 없이 <mark style="background:#ffc4d6">**계정 오탐에도 「허용 목록에 추가」를 제안합니다.**</mark>

```
 - 규칙 조정 제안: 허용 목록에 추가 검토: jiwoo
```

- 7번을 비워 두면 `undo_records` 가 만들어지지 않아 오류가 납니다. 되돌리기도 실행되지 않습니다.

```
NameError: name 'undo_records' is not defined
```

- 8번을 비워 두면 `result` 가 만들어지지 않아 9번 줄에서 오류가 납니다. 파이썬 버전에 따라 뒤에 `Did you mean: …` 이 더 붙을 수 있습니다.

```
NameError: name 'result' is not defined
```

- 9번을 비워 두면 오류 없이 <mark style="background:#ffc4d6">**결과 파일에 0건이 저장됩니다.**</mark> 화면에는 결과가 나오지만 기록이 남지 않습니다.

```
--- 단계 4: fp_results.json 에 0 건 · fp_state_after.json 저장 · 기준 30 분
```

**관제에서는**

- 오탐으로 확인되면 자동 조치를 롤백하고, 사용자에게 알리고, 탐지 규칙이나 허용 목록을 조정(튜닝)하자는 검토 요청을 남깁니다. 규칙 조정은 승인을 받은 뒤에 적용합니다. <mark>롤백한 뒤 실제 상태를 다시 점검하는 복구 확인 단계를 생략하지 않는 것이 중요합니다.</mark> 오늘의 30분 기준은 예시이고, 실제 기준은 팀과 고객사 계약마다 다릅니다.
