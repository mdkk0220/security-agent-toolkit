# 11/13(금) 오후 · 5과목 자동 대응(SOAR) ⑨ — 리스크 평가(risk assessment): 자동 조치별 위험 점수 산출 · 통제 갭 분석 · 평가 문서 작성, 시험 사례를 이용한 Day 4 평가 기준 자동 점검

<mark style="background:#e0d4ff">오전에 리포트 · 승인 게이트 · 오탐 복구를 구현했습니다.</mark> 오후에는 두 가지를 합니다. 하나는 **자동 조치를 운영에 적용하기 전에 위험을 평가한 문서**를 작성하는 일입니다. 다른 하나는 **오늘 만든 기능이 강의계획서의 평가 기준을 충족하는지 자동 점검으로 한 번에 검증**하는 일입니다.

- **5교시**: 자동 조치 6가지마다 영향도(impact, 잘못 실행됐을 때 피해의 크기) × 발생 가능성(likelihood, 잘못 실행될 가능성)으로 위험 점수를 산출하고 등급을 분류합니다. 그다음 등급별로 필요한 통제(control, 컨트롤: 잘못된 실행을 막거나 피해를 줄이거나 나중에 확인하게 하는 장치)가 갖춰져 있는지 비교하는 **통제 갭 분석**(control gap analysis, 컨트롤 갭 애널리시스: 있어야 할 통제와 지금 있는 통제를 비교해 빠진 것을 찾는 일)으로 빠진 통제를 찾아 `risk_assessment.md` 를 작성합니다(`risk_assessment.py`).
- **6교시**: 리포트 반영 · 자동 처리와 승인 요청의 분기 · 오탐 복구, 이 세 가지를 **자동 점검**(automated check, 오토메이티드 체크: 사람이 출력을 읽는 대신 프로그램이 기대한 결과와 실제 결과를 비교하는 방식)으로 한 번에 검증해 `day4_checklist.md` 를 작성하고(`day4_check.py`), 오늘 만든 것을 깃허브에 올립니다.

새 문법은 없습니다. 5교시에서 판다스(pandas, 판다스: 표 모양 데이터를 다루는 파이썬 도구) 표(DataFrame, 데이터프레임)의 두 열(column, 컬럼: 표의 세로 줄) 값을 곱해 새 열을 만드는 일은, <mark style="background:#e0d4ff">오전 2교시에서 두 열 값을 빼서 새 열을 만든 일</mark>과 같은 꼴입니다. 정렬 `sort_values(ascending=False)` 는 <mark style="background:#e0d4ff">4과목에서 배웠습니다</mark>. 여기서는 표(DataFrame)라서 기준이 되는 열 이름 `"score"` 를 앞에 하나 더 씁니다. 보고서의 🔍 질문은 <mark>내 출력 값을 근거로 이유까지</mark> 씁니다. 들여쓰기(줄 앞의 빈칸)는 각 번호 주석과 같은 위치에서 시작합니다. 각 번호 주석 바로 아래에 한 줄을 씁니다. 주석은 지우지 않습니다.

📎 **이전 파일**: <mark style="background:#e0d4ff">5교시는 월요일의 `incident.py` 만 가져와 사용(import)합니다.</mark> <mark style="background:#e0d4ff">6교시는 오전에 만든 코드 파일 `report.py` · `approval_gate.py` · `false_positive.py` 를 가져와 사용(import)합니다.</mark> 오전 데이터 파일(`day05_tickets.json` · `day05_actions.json` · `config/approval_policy.json` · `fp_state.json` · `fp_log.json` · `fp_reports.json`), 오전 2교시가 만든 `incident_report_20261112.md` 를 씁니다. `false_positive.py` 가 부르는 수요일 파일(`rollback.py` 등)도 같은 폴더에 있어야 합니다. 없는 파일은 `complete_files.md` 에서 복사합니다(오전 파일은 8절). `incident.py` 와 수요일 파일은 오전 안내 시작하기의 「🛟 이전 파일이 없을 때」 코드 상자로 만듭니다. 리포트 파일이 없으면 8절의 `day05_2-1_run.py` 를 복사해 한 번 실행하면 생깁니다.

## 시작하기

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** 5과목 폴더로 들어가 오전 파일을 확인합니다. <mark style="background:#bde3ff">`ls` 결과에 `report.py` · `approval_gate.py` · `false_positive.py` · `incident_report_20261112.md` 가 보이면</mark> 됩니다. `incident_report_20261112.md` 가 없으면 `complete_files.md` 8절의 `day05_2-1_run.py` 를 같은 폴더에 새 파일로 붙여 넣고 실행해서 만듭니다.
   ```bash
   pwd
   cd soar_response
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `cd 폴더이름` 그 폴더로 이동 · `ls` 폴더 안의 파일 이름 보기
   - `pwd` 가 이미 `…/soar_response` 로 끝나면 `cd soar_response` 는 건너뜁니다.
3. 오늘 받은 파일 두 개(`day05_pm_risk_check.md`, `day05_pm_report.md`)를 `soar_response` 폴더로 이동하고, 보고서 제목의 `이름` 을 내 이름으로 바꿉니다.
4. **[터미널]** 오전 파일을 불러올 수 있는지 확인합니다(맥북은 `python3`). <mark style="background:#bde3ff">`오전 파일 불러오기 성공` 이 나와야</mark> 합니다.
   ```bash
   python -c "import report, approval_gate, false_positive; print('오전 파일 불러오기 성공')"
   ```

### 🆘 오류가 나면

- `pwd` 가 `soar_response` 로 끝나는지, `ls` 로 <mark>파일 이름이 문서와 같은지</mark> 봅니다.
- <mark style="background:#ffc4d6">`ModuleNotFoundError: No module named 'report'`</mark> 처럼 오전 파일 이름이 나오면 그 파일이 이 폴더에 없다는 뜻입니다. `No module named 'rollback'` 은 <mark style="background:#e0d4ff">수요일 파일</mark>이 없다는 뜻입니다. 위 📎 의 절에서 복사합니다. `No module named 'pandas'` 는 판다스(pandas, 판다스: 표 모양 데이터를 다루는 파이썬 도구)가 설치되어 있지 않다는 뜻입니다. 가상환경이 켜진 터미널에서 `pip install pandas`(판다스를 내려받아 설치하는 명령)를 입력합니다.
- 오류 전체를 친 명령과 함께 AI 에게 붙여 넣어 묻습니다(`.env` · API 키는 지웁니다). 막히면 맨 아래 「정답」을 보고, 풀리지 않으면 보고서에 「모름 — 막힌 곳: …」 이라고 씁니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 <mark>**터미널**에서</mark> 합니다. 실행할 때마다 같은 입력 파일에서 시작해 같은 결과가 나옵니다. 이런 성질을 재현성(reproducibility, 리프로듀서빌리티: 같은 조건에서 다시 실행하면 같은 결과가 나오는 성질)이라고 합니다.

---
# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">5교시 (14:00–14:50) · 자동 조치 6가지의 위험을 점수화하고, 통제 갭 분석으로 빠진 통제를 찾아 리스크 평가 문서 작성하기</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: 이번 주에 계정 잠금 · 세션 종료 · IP 차단 · 티켓 자동 작성 · 담당자 알림 · 상급자 에스컬레이션(escalation, 에스컬레이션: 정해진 시간 안에 처리되지 않은 사건을 상위 담당자에게 넘겨 처리하게 하는 일) 여섯 가지를 자동 조치로 구현했습니다. <mark style="background:#e0d4ff">오전 3교시 승인 게이트는 **요청 한 건마다** 위험을 판정했습니다.</mark> 보안팀장이 「운영에 적용하기 전에 **자동 조치 종류마다** 위험을 평가한 문서를 제출해 주세요」라고 합니다.
> - **문제**: 어떤 자동 조치가 잘못 실행됐을 때 피해가 큰지 정리한 문서가 없습니다. 그 조치에 승인 게이트나 감사 기록 같은 통제가 갖춰져 있는지 정리한 문서도 없습니다. 예를 들어 세션 종료는 되돌릴 수 없는 조치인데, <mark style="background:#ffc4d6">오늘 샘플의 통제 목록에는 세션 종료의 승인 게이트가 빠져 있습니다.</mark> 이렇게 필요한 통제와 지금 있는 통제의 차이를 통제 갭(control gap, 컨트롤 갭)이라고 합니다.
> - **부탁**: 조치마다 ① 영향도와 발생 가능성을 곱해 위험 점수를 산출하고 ② 점수 구간에 따라 높음 · 보통 · 낮음 등급으로 분류한 뒤 ③ <mark>등급별 필수 통제가 빠진 조치를 찾아</mark> `risk_assessment.md` 로 작성해 주세요.
> - **바뀌는 점**: `risk_assessment.md` 16줄이 생성됩니다. 오늘 샘플에서는 <mark style="background:#bde3ff">바로 보완할 조치가 2개</mark>(세션 종료에 승인 게이트, 담당자 알림에 감사 기록)로 산출됩니다. 상황과 숫자는 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다.

### 📖 5.1 리스크 평가는 「영향도 × 발생 가능성」으로 위험을 점수화하고, 등급별로 필요한 통제가 갖춰져 있는지 비교한다

**리스크 평가**(risk assessment, 리스크 어세스먼트: 일이 잘못됐을 때의 피해와 그 일이 일어날 가능성을 따져 위험의 크기를 정하는 일)에서는 위험을 아래 두 값의 조합으로 나타냅니다. NIST SP 800-30(미국 국립표준기술연구소 NIST 가 낸 리스크 평가 지침)도 위험을 위협이 일어날 가능성과 그 결과의 영향이라는 두 요소로 설명합니다. 오늘은 두 값을 모두 <mark style="background:#ffdcb0">1 ~ 3</mark> 의 숫자 척도(scale, 스케일: 등급을 매기는 숫자 범위)로 매깁니다.

| 값 | 뜻 | 오늘의 예 |
|---|---|---|
| **영향도**(impact, 임팩트) | 자동 조치가 잘못 실행됐을 때 업무에 미치는 피해의 크기(심각도). <mark style="background:#ffdcb0">1(작음) ~ 3(큼)</mark> | 계정 잠금은 3: 오탐이면 정상 직원이 로그인하지 못해 업무가 멈춘다 |
| **발생 가능성**(likelihood, 라이클리후드) | 자동 조치가 잘못 실행될 가능성(발생 빈도). <mark style="background:#ffdcb0">1(드묾) ~ 3(잦음)</mark> | 담당자 알림은 3: 오탐 알림도 그대로 보낸다 |
| **위험 점수**(risk score, 리스크 스코어) | 영향도 × 발생 가능성. 1 ~ 9 | <mark style="background:#bde3ff">계정 잠금은 3 × 2 = 6</mark> |

| 위험 등급 | 점수 | 반드시 있어야 하는 통제 |
|---|---|---|
| 높음 | 6 이상 | 승인 게이트 · 감사 기록 |
| 보통 | 3 이상 6 미만 | 감사 기록 |
| 낮음 | 3 미만 | 따로 정하지 않는다 |

- **통제**(control, 컨트롤)는 위험을 줄이는 장치이고, 기능에 따라 세 종류로 나눕니다. **예방 통제**(preventive control, 프리벤티브 컨트롤)는 잘못 실행되기 전에 막습니다(예: 승인 게이트). **교정 통제**(corrective control, 코렉티브 컨트롤)는 잘못 실행된 뒤 피해를 줄이고 원래 상태로 복구합니다(예: 되돌리기). **탐지 통제**(detective control, 디텍티브 컨트롤)는 일어난 일을 나중에 확인할 수 있게 합니다(예: 감사 기록). <mark style="background:#e0d4ff">이번 주에 만든 승인 게이트(오늘 오전) · 되돌리기(수요일) · 허용 목록(수요일) · 감사 기록(월요일) · 알림 간격(목요일)</mark>이 모두 통제입니다.
- 세션 종료는 되돌릴 수 없어서 교정 통제(되돌리기)를 쓸 수 없습니다. 그래서 <mark>잘못 실행되기 전에 막는 예방 통제(승인 게이트)가 더 중요합니다.</mark>
- 영향도와 발생 가능성의 숫자, 그리고 <mark style="background:#ffdcb0">등급 기준(6 이상 높음, 3 이상 보통)</mark>은 팀이 위험 허용 수준(risk tolerance, 리스크 톨러런스: 조직이 받아들일 수 있다고 정한 위험의 크기)에 맞춰 회의로 정합니다. 오늘 파일의 숫자와 통제 목록은 예시입니다. 통제를 적용한 뒤에도 남는 위험을 잔여 위험(residual risk, 레지듀얼 리스크)이라고 하는데, 오늘 코드는 잔여 위험을 계산하지 않고 필수 통제가 빠졌는지만 비교합니다.

함수 다섯 개와 실행 파일 가운데 직접 쓰는 곳은 **아홉 군데**입니다.

```
risk_assessment.py   make_risk_table        : 표로 바꾸고 위험 점수 열을 더한다 (1번)
                     risk_level             : 6 이상이면 (2번) 높음을 리턴한다 (3번). 보통 · 낮음은 미리 채움
                     find_missing_controls  : 있어야 하는 통제가 없으면 (4번) 추가한다 (5번)
                     assess_risks           : 점수가 큰 것부터 정렬하고 (6번), 조치마다 빠진 통제를 찾는다 (7번)
                     make_assessment_lines  : 리스크 평가 문서의 줄 리스트를 만든다 (미리 채움)
실행 파일            day05_5-1_run.py       : 평가 결과를 받아 (8번), 빠진 통제가 있는 조치를 센다 (9번)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 5-1 · 자동 조치 6가지의 위험 점수 · 등급 · 빠진 통제로 리스크 평가 문서 쓰기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>자동 조치마다 위험이 얼마나 큰지, 필요한 통제가 갖춰져 있는지 정리한 리스크 평가 문서가 없습니다</mark>.
- **만드는 것**: 위험 점수 산출 · 등급 분류 · 통제 갭 분석 · 위험도순 정렬(`risk_assessment.py`), 평가 결과 출력과 리스크 평가 문서 저장(`day05_5-1_run.py`).
- **실행하면**: <mark style="background:#bde3ff">단계 1: 불러온 자동 조치 수, 단계 2: 점수가 큰 조치부터 등급과 빠진 통제, 단계 3: 바로 보완할 조치 수와 저장한 문서가 나옵니다.</mark>

**🎯 할 일**: 데이터 파일 하나와 코드 파일 두 개를 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행한 뒤 문서 파일을 열어 읽습니다.

**`config/automation_risks.json`** — 자동 조치 6가지의 영향도 · 발생 가능성 · 지금 있는 통제(existing control, 이그지스팅 컨트롤: 이미 적용된 통제)를 적은 입력 데이터입니다.

```
[
  {"action": "계정 잠금", "impact": 3, "likelihood": 2, "controls": ["승인 게이트", "되돌리기", "감사 기록", "VIP 예외"]},
  {"action": "세션 종료", "impact": 3, "likelihood": 2, "controls": ["감사 기록"]},
  {"action": "IP 차단", "impact": 3, "likelihood": 2, "controls": ["허용 목록", "승인 게이트", "자동 해제", "되돌리기", "감사 기록"]},
  {"action": "티켓 자동 작성", "impact": 1, "likelihood": 2, "controls": ["병합", "감사 기록"]},
  {"action": "담당자 알림", "impact": 1, "likelihood": 3, "controls": ["알림 간격", "재시도"]},
  {"action": "상급자 에스컬레이션", "impact": 2, "likelihood": 1, "controls": ["같은 단계 한 번"]}
]
```

**`risk_assessment.py`** — 리스크 평가 함수 모음입니다. 직접 쓰는 곳은 1 ~ 7번입니다.

- 2번과 3번은 `if` 한 줄과 그 안의 `return` 한 줄입니다. 그 아래 미리 채운 `if score >= 3:` 은 2번과 같은 들여쓰기입니다.

```python
import pandas as pd                                                         # 표를 다루기 위해 판다스를 pd 라는 이름으로 불러온다

REQUIRED_CONTROLS = {                                                       # 위험 등급마다 반드시 있어야 하는 통제
    "높음": ["승인 게이트", "감사 기록"],                                   # 잘못되면 피해가 큰 조치
    "보통": ["감사 기록"],                                                  # 나중에 확인할 수 있어야 하는 조치
    "낮음": [],                                                             # 따로 요구하지 않는다
}


def make_risk_table(risks):                                                 # 자동 조치마다 적은 위험 리스트를 받는 함수
    """위험 리스트를 표(DataFrame)로 바꾸고, 영향도 × 발생 가능성으로 위험 점수(score) 열을 더해 리턴한다.
    자동 조치마다 위험이 얼마나 큰지 숫자 하나로 비교할 때 쓴다.
    """
    table = pd.DataFrame(risks)                                             # 위험 리스트를 표로 바꾼다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. table["impact"] * table["likelihood"] 를 table["score"] 에 담는다 (위험 점수)
    return table                                                            # 점수 열을 더한 표를 리턴한다 — 미리 채운 줄


def risk_level(score):                                                      # 위험 점수를 받는 함수
    """위험 점수가 6 이상이면 「높음」, 3 이상이면 「보통」, 그보다 낮으면 「낮음」을 리턴한다.
    점수를 사람이 읽기 쉬운 등급으로 바꿀 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. score 가 6 이상이면 (if, >=)
        # 3. "높음" 을 리턴한다
    if score >= 3:                                                          # 3 이상이면 — 미리 채운 줄
        return "보통"                                                       # 보통을 리턴한다 — 미리 채운 줄
    return "낮음"                                                           # 그보다 낮으면 낮음을 리턴한다 — 미리 채운 줄


def find_missing_controls(level, controls):                                 # 위험 등급과 지금 있는 통제 리스트를 받는 함수
    """그 등급에 반드시 있어야 하는 통제 가운데 지금 없는 것을 리스트로 리턴한다.
    위험이 큰 자동 조치에 승인이나 되돌리기 같은 통제가 빠졌는지 찾을 때 쓴다.
    """
    missing = []                                                            # 빠진 통제를 모을 빈 리스트 — 미리 채운 줄
    required = REQUIRED_CONTROLS[level]                                     # 이 등급에 반드시 있어야 하는 통제 — 미리 채운 줄
    for control in required:                                                # 있어야 하는 통제를 하나씩 꺼낸다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 4. control 이 controls 안에 없으면 (if, not in)
            # 5. missing 에 control 을 추가한다 (append)
    return missing                                                          # 빠진 통제 리스트를 리턴한다 — 미리 채운 줄


def assess_risks(table):                                                    # 점수 열이 있는 위험 표를 받는 함수
    """점수가 큰 조치부터 정렬하고, 조치마다 등급과 빠진 통제를 붙인 딕셔너리 리스트를 리턴한다.
    리스크 평가 문서에 위험이 큰 조치부터 적을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 6. table.sort_values("score", ascending=False) 를 sorted_table 에 담는다 (점수가 큰 것부터)
    rows = []                                                               # 평가 결과를 모을 빈 리스트 — 미리 채운 줄
    for row in sorted_table.to_dict("records"):                             # 표를 딕셔너리 리스트로 바꿔 하나씩 꺼낸다 — 미리 채운 줄
        level = risk_level(row["score"])                                    # 점수로 등급을 정한다 — 미리 채운 줄
        # 7. find_missing_controls(level, row["controls"]) 의 결과를 missing 에 담는다
        row["level"] = level                                                # 등급을 딕셔너리에 넣는다 — 미리 채운 줄
        row["missing"] = missing                                            # 빠진 통제를 딕셔너리에 넣는다 — 미리 채운 줄
        rows.append(row)                                                    # 평가 결과를 추가한다 — 미리 채운 줄
    return rows                                                             # 평가 결과 리스트를 리턴한다 — 미리 채운 줄


def make_assessment_lines(rows):                                            # 평가 결과 리스트를 받는 함수
    """평가 결과로 리스크 평가 문서(마크다운)의 줄 리스트를 만들어 리턴한다.
    자동 조치를 운영에 넣기 전에 팀이 함께 읽을 문서를 쓸 때 쓴다.
    """
    lines = ["# 자동 대응 리스크 평가 — 2026-11-13(금)", ""]                # 제목과 빈 줄로 시작한다
    lines.append("- 점수 = 영향도(1~3) × 발생 가능성(1~3). 6 이상 높음, 3 이상 보통, 그 밖은 낮음")  # 기준을 적는다
    lines.append("")                                                        # 빈 줄
    lines.append("| 자동 조치 | 영향도 | 발생 가능성 | 점수 | 등급 | 지금 있는 통제 | 빠진 통제 |")  # 표의 제목 줄
    lines.append("|---|---|---|---|---|---|---|")                           # 표의 구분 줄
    for row in rows:                                                        # 평가 결과를 하나씩 꺼낸다
        controls_text = ", ".join(row["controls"])                          # 지금 있는 통제를 쉼표로 잇는다
        missing_text = ", ".join(row["missing"])                            # 빠진 통제를 쉼표로 잇는다
        if missing_text == "":                                              # 빠진 통제가 없으면
            missing_text = "없음"                                           # 없음이라고 적는다
        numbers = str(row["impact"]) + " | " + str(row["likelihood"]) + " | " + str(row["score"])  # 영향도 · 발생 가능성 · 점수를 표 모양으로 잇는다
        lines.append("| " + row["action"] + " | " + numbers + " | " + row["level"] + " | " + controls_text + " | " + missing_text + " |")  # 표의 한 줄
    lines.append("")                                                        # 빈 줄
    lines.append("## 바로 보완할 조치")                                     # 보완할 조치 절의 제목
    for row in rows:                                                        # 평가 결과를 하나씩 꺼낸다
        if row["missing"] != []:                                            # 빠진 통제가 있으면
            gap_text = ", ".join(row["missing"])                            # 빠진 통제를 쉼표로 잇는다
            lines.append("- " + row["action"] + ": " + gap_text + " 추가")  # 보완할 내용을 적는다
    return lines                                                            # 완성한 줄 리스트를 리턴한다
```

**`day05_5-1_run.py`** — 8 · 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다.

```python
from incident import load_json                                                             # 월요일 파일의 JSON 읽기 함수를 불러온다
from risk_assessment import make_risk_table, assess_risks, make_assessment_lines           # 방금 만든 리스크 평가 함수를 불러온다

DOC_PATH = "risk_assessment.md"                                                            # 리스크 평가 문서를 저장할 파일 이름

risks = load_json("config/automation_risks.json")                                          # 자동 조치마다 적은 위험 파일을 리스트로 읽는다
print("--- 단계 1: 불러온 자동 조치", len(risks), "개")                                    # 단계 1 시작을 알리는 줄

table = make_risk_table(risks)                                                             # 표로 바꾸고 점수 열을 더한다
# ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
# 8. assess_risks(table) 의 결과를 rows 에 담는다
print("--- 단계 2: 점수가 큰 조치부터")                                                    # 단계 2 시작을 알리는 줄
gap_count = 0                                                                              # 빠진 통제가 있는 조치 수 : 처음에는 0
for row in rows:                                                                           # 평가 결과를 하나씩 꺼낸다
    print(row["action"], "· 점수", row["score"], "·", row["level"], "· 빠진 통제", row["missing"])  # 조치 한 줄을 출력한다
    if row["missing"] != []:                                                               # 빠진 통제가 있으면
        # 9. gap_count 에 gap_count + 1 을 담는다 (1 늘린다)

lines = make_assessment_lines(rows)                                                        # 문서의 줄 리스트를 만든다
text = "\n".join(lines) + "\n"                                                             # 줄 리스트를 줄바꿈으로 이어 한 문자열로 만든다
with open(DOC_PATH, "w", encoding="utf-8") as doc_file:                                    # 문서 파일을 쓰기 모드("w")로 연다
    doc_file.write(text)                                                                   # 문서 문자열을 파일에 쓴다
print("--- 단계 3: 바로 보완할 조치", gap_count, "개 ·", DOC_PATH, len(lines), "줄 저장")  # 단계 3 시작을 알리는 줄
```

**순서**

1. **[터미널]** 파일 세 개를 만들고 **[VS Code]** 에서 열어 붙여 넣습니다.
   ```bash
   pwd
   touch config/automation_risks.json risk_assessment.py day05_5-1_run.py
   ls config
   ```
2. **[VS Code]** `risk_assessment.py` 1 ~ 7번, `day05_5-1_run.py` 8 · 9번을 씁니다. 막히면 아래 「5교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 가 `soar_response` 로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   python day05_5-1_run.py
   ```
4. 출력은 세 단계입니다. 제목 줄은 줄 수에 넣지 않습니다.
   - 단계 1 과 단계 3 은 숫자가 제목 줄에 함께 나와 그 아래 줄이 없습니다.
   - 단계 2 는 조치 6개가 한 줄씩, 모두 6줄입니다.
5. **[VS Code]** 왼쪽 목록에서 `risk_assessment.md` 를 열고 `Ctrl+Shift+V`(맥북은 `Cmd+Shift+V`)로 마크다운 미리보기에서 표 모양을 확인합니다. <mark style="background:#bde3ff">표 한 개와 「바로 보완할 조치」 절이 보이면</mark> 됩니다.
6. **[보고서]** `day05_pm_report.md` 의 `## 5교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 등급이 높음인 조치와 바로 보완할 조치 2개를 적어 주세요.
   - (나) 🔍 계정 잠금 · 세션 종료 · IP 차단은 점수가 모두 6(높음)인데, 세션 종료만 통제 갭이 있습니다. `config/automation_risks.json` 의 `controls` 를 근거로 그 이유를 적고, 세션 종료에 예방 통제인 승인 게이트가 특히 필요한 이유를 수요일의 되돌리기(교정 통제)와 연결해 적어 주세요.
   - (다) 🔍 담당자 알림은 영향도가 1인데 등급이 보통입니다. 점수 계산을 근거로 그 이유를 적고, 탐지 통제인 감사 기록이 없으면 사고가 난 뒤 무엇을 확인할 수 없는지 적어 주세요.

### 5교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 두 열을 곱해 위험 점수 열 만들기 | `table["score"] = table["impact"] * table["likelihood"]` |
| 점수가 기준 이상이면 등급 문자열 리턴 | `if score >= 6:` → `return "높음"` |
| 필수 통제가 없으면 빠진 통제 리스트에 추가 | `if control not in controls:` → `missing.append(control)` |
| 위험 점수가 큰 순서로 정렬 | `sorted_table = table.sort_values("score", ascending=False)` |
| 함수 결과를 변수에 저장하기 | `missing = find_missing_controls(level, row["controls"])` |
| 빠진 통제가 있는 조치 수를 1 늘리기 | `gap_count = gap_count + 1` |

---
# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">6교시 (15:00–15:50) · 평가 기준 세 가지를 시험 사례와 자동 점검으로 한 번에 검증해 Day 4 점검 목록 만들기</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: <mark style="background:#e0d4ff">오늘 오전에 리포트 · 승인 게이트 · 오탐 복구를 따로 구현하고</mark> 하나씩 실행해 출력을 사람이 읽어 검증했습니다(수동 검증). 강의계획서의 Day 4 평가 기준은 <mark style="background:#ffdcb0">① 2 · 3일 차 데이터가 리포트에 빠짐없이 들어갔는가 ② 위험에 따라 자동 · 승인이 맞게 나뉘는가 ③ 오탐 복구가 신속하고 완전한가</mark>, 세 가지입니다. 오늘 점검 프로그램은 ①을 「티켓 번호와 티켓 없는 조치의 인시던트 번호가 리포트에 들어 있는가」로 판정합니다.
> - **문제**: 출력을 사람이 읽는 수동 검증만으로는 승인 기준 숫자를 바꾸거나 리포트 틀을 고친 뒤에 <mark style="background:#ffc4d6">무엇이 달라졌는지 놓치기 쉽습니다.</mark> 예를 들어 <mark style="background:#ffdcb0">승인 기준을 3점에서 4점으로 올리면</mark> `REQ-5`(함께 쓰는 IP, 3점)의 결정이 승인 필요에서 「자동」으로 바뀌는데, 출력 8줄을 다시 읽어야 알 수 있습니다. 변경 뒤에는 같은 점검을 다시 실행해 결과를 비교하는 방법이 필요합니다.
> - **부탁**: 세 기준을 한 번에 검증하는 점검 프로그램을 만들어 주세요. 승인 게이트는 <mark>기대한 결정(기대 결과)을 미리 적어 둔 시험 사례 7개로 검증해 주세요.</mark>
> - **바뀌는 점**: 실행 한 번으로 점검 목록 `day4_checklist.md` 5줄이 생성되고, 오늘 샘플에서는 <mark style="background:#bde3ff">세 기준이 모두 「통과」</mark>입니다. 기준을 지키지 못하면 <mark style="background:#ffc4d6">「확인 필요」와 문제 문장</mark>이 나옵니다. 상황과 숫자는 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다.

### 📖 6.1 자동 점검은 「기대한 결과를 미리 적어 두고, 실제 결과와 하나씩 비교하는」 검증이다

| 기준 | 기대한 결과(미리 적어 둔 것) | 실제 결과 | 불일치로 남기는 것(문제 목록) |
|---|---|---|---|
| ① 리포트 반영 | 티켓 번호 7개 + 티켓 없는 조치의 인시던트 번호 1개 | <mark style="background:#e0d4ff">오전 2교시가 쓴 `incident_report_20261112.md`</mark> 의 본문 | 리포트에 없는 번호 (1 · 2번) |
| ② 자동 · 승인 분기 | `gate_cases.json` 의 사례마다 기대한 결정 | <mark style="background:#e0d4ff">오전 3교시 `decide_gate`</mark> 의 결정 | 기대와 다른 사례 (3 · 4번) |
| ③ 오탐 복구 | <mark style="background:#ffdcb0">남은 대상 0개 · 30분 안</mark> · 정탐(진짜 공격) 계정 `dami` 는 잠김 유지 | <mark style="background:#e0d4ff">오전 4교시 `handle_false_positive`</mark> 의 결과와 처리 뒤 상태 | 복구 안 된 대상 · 시간 초과(5번) · 잠금이 풀린 정탐 계정(6 · 7번) |

- **시험 사례**(test case, 테스트 케이스: 입력과 기대한 결과를 짝지어 적어 둔 것)는 **경계값 분석**(boundary value analysis, 바운더리 밸류 애널리시스: 기준 숫자 바로 앞뒤의 값, 즉 경계값으로 시험 사례를 만드는 방법)에 따라 경계의 양쪽을 꼭 포함합니다. 오늘은 대상 3개(1점, 자동)와 대상 4개(3점, 승인 필요)를 함께 포함해 <mark style="background:#ffdcb0">「4개 이상」 경계</mark>를 검증합니다. 경계에서는 `>` 를 `>=` 로 잘못 쓰는 경계 조건 오류(화요일에 배운 off-by-one error)가 가장 잘 드러나기 때문입니다.
- 리포트 점검은 번호 문자열이 리포트 본문 안에 포함되어 있는지(`in`)로 판정합니다. 번호의 포함 여부만 검사하고, <mark style="background:#ffc4d6">줄의 모양(형식)은 검사하지 않습니다.</mark>
- 오탐 복구 점검은 <mark style="background:#e0d4ff">오전 4교시와 같은 입력으로 다시 처리한 결과</mark>를 대상으로 합니다. 같은 입력이면 같은 결과가 나오므로(재현성) 오전 4교시 출력과 같은 결과가 나와야 합니다.
- 기준 숫자나 코드를 바꾼 뒤 같은 점검을 다시 실행해, 이전에 맞던 결과가 그대로 맞는지 확인하는 방식을 **회귀 시험**(regression test, 리그레션 테스트: 변경 뒤에 기존에 되던 것이 깨지지 않았는지 다시 확인하는 시험)이라고 합니다. 오늘의 점검 프로그램은 이 회귀 시험으로 쓸 수 있습니다.

**`gate_cases.json`** — 승인 게이트 시험 사례 7개입니다. `case` 는 사례 이름, `expected` 는 기대한 결정(기대 결과), `request` 는 <mark style="background:#e0d4ff">오전 3교시 요청</mark>에서 `incident` 만 뺀 형식의 조치 요청입니다.

```
[
  {"case": "high 등급 한 명", "expected": "자동", "request": {"id": "T-1", "action": "계정 잠금", "target": "dami", "grade": "high", "users_on_ip": 0, "target_count": 1}},
  {"case": "VIP 계정", "expected": "승인 필요", "request": {"id": "T-2", "action": "계정 잠금", "target": "gaeun", "grade": "low", "users_on_ip": 0, "target_count": 1}},
  {"case": "함께 쓰는 IP", "expected": "승인 필요", "request": {"id": "T-3", "action": "IP 차단", "target": "198.51.100.77", "grade": "mid", "users_on_ip": 2, "target_count": 1}},
  {"case": "대상 4개", "expected": "승인 필요", "request": {"id": "T-4", "action": "계정 잠금", "target": "minsu", "grade": "mid", "users_on_ip": 0, "target_count": 4}},
  {"case": "대상 3개", "expected": "자동", "request": {"id": "T-5", "action": "계정 잠금", "target": "minsu", "grade": "mid", "users_on_ip": 0, "target_count": 3}},
  {"case": "허용 목록 IP", "expected": "차단 금지", "request": {"id": "T-6", "action": "IP 차단", "target": "203.0.113.80", "grade": "high", "users_on_ip": 4, "target_count": 1}},
  {"case": "점검 서버", "expected": "차단 금지", "request": {"id": "T-7", "action": "IP 차단", "target": "192.0.2.10", "grade": "low", "users_on_ip": 0, "target_count": 1}}
]
```

함수 네 개와 실행 파일 가운데 직접 쓰는 곳은 **아홉 군데**입니다.

```
day4_check.py   check_report    : 있어야 할 번호가 리포트에 없으면 (1번) 추가한다 (2번)
                check_gate      : 사례마다 결정을 받아 (3번) 기대와 다르면 (4번) 남긴다
                check_recovery  : 시간 안에 끝나지 않았거나 (5번) 진짜 공격 계정이 풀렸으면 (6 · 7번) 남긴다
                mark            : 문제가 없으면 「통과」, 있으면 「확인 필요」를 리턴한다 (미리 채움)
실행 파일       day05_6-1_run.py : 리포트 점검 결과 (8번) · 오탐 복구 점검 결과 (9번)를 받아 점검 목록을 쓴다
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 6-1 · 평가 기준 세 가지를 한 번에 점검해 Day 4 점검 목록 쓰기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>리포트 · 승인 게이트 · 오탐 복구가 기준을 충족하는지 사람이 출력을 하나씩 읽어 수동으로 검증합니다</mark>.
- **만드는 것**: 리포트 반영 · 승인 게이트 분기 · 오탐 복구 점검 함수(`day4_check.py`), 점검 목록 출력과 저장(`day05_6-1_run.py`).
- **실행하면**: <mark style="background:#bde3ff">단계 1: 점검 재료의 수, 단계 2: 기준마다 「통과」 또는 「확인 필요」와 문제 수, 단계 3: 저장한 점검 목록이 나옵니다.</mark>

**🎯 할 일**: 데이터 파일 하나와 코드 파일 두 개를 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행해서 단계 2 를 읽습니다.

**`day4_check.py`** — 점검 함수 모음입니다. 직접 쓰는 곳은 1 ~ 7번입니다.

- 4번과 5번은 `if` 한 줄만 씁니다. 그 아래 미리 채운 `append` 줄이 `if` 안쪽입니다.

```python
from report import find_missing_incidents                        # 오전 2교시의 티켓 없는 조치 찾기 함수를 불러온다
from approval_gate import decide_gate                            # 오전 3교시의 승인 게이트 함수를 불러온다


def check_report(report_text, tickets, actions):                 # 리포트 문자열 · 티켓 리스트 · 조치 기록 리스트를 받는 함수
    """리포트에 들어 있어야 할 티켓 번호와 티켓 없는 조치의 인시던트 번호 가운데, 리포트에 없는 번호를 리스트로 리턴한다.
    고객사에 리포트를 보내기 전에 2 · 3일 차 데이터가 빠짐없이 들어갔는지 확인할 때 쓴다.
    """
    expected = []                                                # 리포트에 있어야 할 번호를 모을 빈 리스트 — 미리 채운 줄
    for ticket in tickets:                                       # 티켓을 하나씩 꺼낸다 — 미리 채운 줄
        expected.append(ticket["id"])                            # 티켓 번호를 추가한다 — 미리 채운 줄
    for action in find_missing_incidents(actions, tickets):      # 티켓이 없는 조치를 하나씩 꺼낸다 — 미리 채운 줄
        expected.append(action["incident"])                      # 그 인시던트 번호를 추가한다 — 미리 채운 줄
    not_found = []                                               # 리포트에 없는 번호를 모을 빈 리스트 — 미리 채운 줄
    for number in expected:                                      # 있어야 할 번호를 하나씩 꺼낸다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 1. number 가 report_text 안에 없으면 (if, not in)
            # 2. not_found 에 number 를 추가한다 (append)
    return not_found                                             # 리포트에 없는 번호 리스트를 리턴한다 — 미리 채운 줄


def check_gate(cases, policy):                                   # 시험 사례 리스트와 승인 정책을 받는 함수
    """시험 사례마다 승인 게이트를 실행해, 결정이 기대한 결정과 다른 사례의 이름을 리스트로 리턴한다.
    승인 기준을 바꾼 뒤에도 자동 · 승인 필요 · 차단 금지가 맞게 나뉘는지 확인할 때 쓴다.
    """
    wrong = []                                                   # 기대와 다른 사례를 모을 빈 리스트 — 미리 채운 줄
    for case in cases:                                           # 시험 사례를 하나씩 꺼낸다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. decide_gate(case["request"], policy) 의 두 결과를 decision, reasons 에 담는다
        # 4. decision 이 case["expected"] 와 다르면 (if, !=)
            wrong.append(case["case"] + " (기대 " + case["expected"] + ", 결과 " + decision + ")")  # 사례 이름과 두 결정을 추가한다 — 미리 채운 줄
    return wrong                                                 # 기대와 다른 사례 리스트를 리턴한다 — 미리 채운 줄


def check_recovery(results, state, true_positive_users):         # 오탐 처리 결과 · 처리 뒤 상태 · 진짜 공격 계정 리스트를 받는 함수
    """오탐 처리 결과에서 남은 대상 · 시간 초과를 찾고, 진짜 공격 계정이 풀렸는지도 확인해 문제 문장 리스트를 리턴한다.
    오탐 복구가 신속하고 완전했는지, 진짜 공격의 조치는 그대로인지 확인할 때 쓴다.
    """
    problems = []                                                # 문제 문장을 모을 빈 리스트 — 미리 채운 줄
    for result in results:                                       # 오탐 처리 결과를 하나씩 꺼낸다 — 미리 채운 줄
        if result["remaining"] != []:                            # 아직 복구되지 않은 대상이 있으면 — 미리 채운 줄
            problems.append(result["incident"] + " 복구 안 됨")  # 문제를 추가한다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. result["in_time"] 이 False 이면 (if not)
            problems.append(result["incident"] + " 30분 넘음")   # 문제를 추가한다 — 미리 채운 줄
    for user in true_positive_users:                             # 진짜 공격 계정을 하나씩 꺼낸다 — 미리 채운 줄
        # 6. user 가 state["locked_users"] 안에 없으면 (if, not in)
            # 7. problems 에 user + " 잠금이 풀림" 을 추가한다 (append)
    return problems                                              # 문제 문장 리스트를 리턴한다 — 미리 채운 줄


def mark(problems):                                              # 문제 리스트를 받는 함수
    """문제 리스트가 비어 있으면 「통과」, 하나라도 있으면 「확인 필요」를 리턴한다.
    점검 결과를 한눈에 보이게 출력할 때 쓴다.
    """
    if problems == []:                                           # 문제가 없으면
        return "통과"                                            # 통과를 리턴한다
    return "확인 필요"                                           # 문제가 있으면 확인 필요를 리턴한다
```

**`day05_6-1_run.py`** — 8 · 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다.

```python
from incident import load_json                                                              # 월요일 파일의 JSON 읽기 함수를 불러온다
from false_positive import handle_false_positive                                            # 오전 4교시의 오탐 처리 함수를 불러온다
from day4_check import check_report, check_gate, check_recovery, mark                       # 방금 만든 점검 함수를 불러온다

REPORT_PATH = "incident_report_20261112.md"                                                 # 오전 2교시가 만든 리포트 파일 이름
TRUE_POSITIVE_USERS = ["dami"]                                                              # 진짜 공격으로 확인된 계정 (오탐 처리로 풀면 안 된다)
NOW = 45                                                                                    # 오탐 신고를 처리하는 지금 시각(분)

tickets = load_json("day05_tickets.json")                                                   # 목요일 근무의 티켓 파일을 읽는다
actions = load_json("day05_actions.json")                                                   # 목요일 근무의 조치 기록 파일을 읽는다
policy = load_json("config/approval_policy.json")                                           # 승인 정책 파일을 읽는다
cases = load_json("gate_cases.json")                                                        # 승인 게이트 시험 사례 파일을 읽는다
print("--- 단계 1: 점검 재료 · 티켓", len(tickets), "장 · 조치 기록", len(actions), "건 · 시험 사례", len(cases), "개")  # 단계 1 시작을 알리는 줄

with open(REPORT_PATH, encoding="utf-8") as report_file:                                    # 리포트 파일을 읽기 모드로 연다
    report_text = report_file.read()                                                        # 파일 내용을 한 문자열로 읽는다
# ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
# 8. check_report(report_text, tickets, actions) 의 결과를 report_problems 에 담는다
gate_problems = check_gate(cases, policy)                                                   # 승인 게이트 점검

state = load_json("fp_state.json")                                                          # 오탐 처리 전 연습용 시스템 상태를 읽는다
log = load_json("fp_log.json")                                                              # 자동 조치 기록을 읽는다
results = []                                                                                # 오탐 처리 결과를 담을 빈 리스트
for report in load_json("fp_reports.json"):                                                 # 오탐 신고를 하나씩 꺼낸다
    result = handle_false_positive(report, log, state, NOW)                                 # 신고 한 건을 처리한다
    results.append(result)                                                                  # 처리 결과를 추가한다
# 9. check_recovery(results, state, TRUE_POSITIVE_USERS) 의 결과를 recovery_problems 에 담는다

checks = [                                                                                  # 강의계획서 Day 4 평가 기준마다 점검 결과
    {"title": "① 2 · 3일 차 데이터가 리포트에 빠짐없이 들어갔다", "problems": report_problems},  # 리포트 점검
    {"title": "② 위험 점수에 따라 자동 · 승인 필요 · 차단 금지가 맞게 나뉜다", "problems": gate_problems},  # 승인 게이트 점검
    {"title": "③ 오탐 복구가 30분 안에 빠짐없이 끝났고 진짜 공격의 잠금은 그대로다", "problems": recovery_problems},  # 오탐 복구 점검
]
print("--- 단계 2: Day 4 점검 목록")                                                        # 단계 2 시작을 알리는 줄
lines = ["# Day 4 마무리 점검 — 2026-11-13(금)", ""]                                        # 점검 문서의 제목과 빈 줄
for check in checks:                                                                        # 점검 결과를 하나씩 꺼낸다
    result_mark = mark(check["problems"])                                                   # 통과인지 확인 필요인지 정한다
    print("[" + result_mark + "]", check["title"], "· 문제", len(check["problems"]), "개")  # 점검 한 줄을 출력한다
    lines.append("- [" + result_mark + "] " + check["title"])                               # 점검 문서에 한 줄을 추가한다
    for problem in check["problems"]:                                                       # 문제 문장을 하나씩 꺼낸다
        print("   -", problem)                                                              # 문제를 출력한다
        lines.append("  - " + problem)                                                      # 점검 문서에 문제를 추가한다

text = "\n".join(lines) + "\n"                                                              # 줄 리스트를 줄바꿈으로 이어 한 문자열로 만든다
with open("day4_checklist.md", "w", encoding="utf-8") as check_file:                        # 점검 문서 파일을 쓰기 모드("w")로 연다
    check_file.write(text)                                                                  # 점검 문서를 파일에 쓴다
print("--- 단계 3: day4_checklist.md", len(lines), "줄 저장")                               # 단계 3 시작을 알리는 줄과 저장한 줄 수
```

**순서**

1. **[터미널]** 파일 세 개를 만들고 **[VS Code]** 에서 열어 붙여 넣습니다.
   ```bash
   pwd
   touch gate_cases.json day4_check.py day05_6-1_run.py
   ls
   ```
2. **[VS Code]** `day4_check.py` 1 ~ 7번, `day05_6-1_run.py` 8 · 9번을 씁니다. 막히면 아래 「6교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 가 `soar_response` 로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   python day05_6-1_run.py
   ```
4. 출력은 세 단계입니다. 제목 줄은 줄 수에 넣지 않습니다.
   - 단계 1 과 단계 3 은 숫자가 제목 줄에 함께 나와 그 아래 줄이 없습니다.
   - 단계 2 는 기준마다 한 줄씩 3줄입니다. 문제가 있으면 문제마다 한 줄이 더 나옵니다.
5. **[보고서]** `day05_pm_report.md` 의 `## 6교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 세 기준의 결과와 `day4_checklist.md` 의 줄 수를 적어 주세요.
   - (나) 🔍 `gate_cases.json` 에는 「대상 3개」와 「대상 4개」 사례가 함께 있습니다. 두 사례의 점수와 기대한 결정을 근거로, 경계값 분석에 따라 기준 숫자 바로 앞뒤 값(경계값)의 사례를 함께 넣는 이유를 적어 주세요.
   - (다) 🔍 ③ 기준은 오탐 신고를 처리한 뒤에도 정탐 계정 `dami` 의 잠금이 유지되는지 확인합니다. 오탐 복구 점검에 이 확인이 없으면 어떤 실수를 놓칠 수 있는지 적어 주세요. 수요일의 `rollback_incident`(오전 4교시가 가져와 사용(import)하는 함수)가 어떻게 동작할 때 그 실수가 생기는지도 함께 적어 주세요.

### 6교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 문자열 안에 없으면 | `if number not in report_text:` |
| 두 결과를 함께 받기 | `decision, reasons = decide_gate(case["request"], policy)` |
| 다르면 | `if decision != case["expected"]:` |
| 거짓이면 | `if not result["in_time"]:` |
| 리스트 안에 없으면 | `if user not in state["locked_users"]:` |
| 문자열을 이어 붙여 추가 | `problems.append(user + " 잠금이 풀림")` |
| 함수 결과를 변수에 저장하기 | `report_problems = check_report(report_text, tickets, actions)` |

---

### 마무리 · 오늘 만든 것을 깃허브에 올리기

<mark>문제가 아니라 오늘 한 일을 저장소에 올리는 마무리입니다.</mark> 6교시 마지막 약 10분에 합니다. 어느 터미널을 써도 됩니다. 먼저 `pwd` 로 위치를 확인하고, 결과가 `soar_response` 로 끝나면 아래 1번의 `cd ..` 를 칩니다.

**📍 이런 상황이 있습니다**

- **지금은**: <mark>팀장이 「오늘 만든 리포트 · 승인 게이트 · 오탐 복구 · 리스크 평가 · 점검 코드와 문서를 저장소에 남겨 달라」고 합니다</mark>.
- **그래서 하는 것**: `git status` 로 올라갈 파일을 확인한 뒤(`.env` 같은 비밀 키 파일이 섞이면 안 됩니다) `git add` → `git commit` → `git push` 순서로 올립니다.
- **끝나면**: 깃허브 저장소의 `soar_response` 폴더에 `report.py` · `approval_gate.py` · `false_positive.py` · `risk_assessment.py` · `day4_check.py` 와 `incident_report_20261112.md` · `risk_assessment.md` · `day4_checklist.md` 가 보입니다.

**순서**

0. **[터미널]** 오늘 만든 파일이 있는지 `soar_response` 폴더에서 확인합니다. 두 명령을 하나씩 칩니다. `day05_am_report.md` 와 `day05_pm_report.md` 의 모든 질문에서 `답:` 뒤와 코드 상자가 모두 채워졌는지도 확인합니다(마무리 (가)는 3번에서 채웁니다).

   ① 지금 위치를 확인합니다.

   ```bash
   pwd
   ```

   - 하는 일: 지금 있는 폴더의 위치를 보여 줍니다.
   - 나오는 것: <mark style="background:#bde3ff">`soar_response` 로 끝나야</mark> 합니다.

   ② 폴더 안의 파일을 봅니다.

   ```bash
   ls
   ```

   - 하는 일: 폴더 안의 파일 이름을 보여 줍니다.
   - 나오는 것: `report.py` · `approval_gate.py` · `false_positive.py` · `risk_assessment.py` · `day4_check.py` · `incident_report_20261112.md` · `risk_assessment.md` · `day4_checklist.md` · `config` 가 보이면 됩니다.

1. **[터미널]** `security-agent-toolkit` 폴더로 이동합니다. 0번의 `pwd` 결과가 `soar_response` 로 끝날 때만 `cd ..` 를 칩니다. 이미 `…/security-agent-toolkit` 으로 끝나면 `cd ..` 는 건너뛰고 `pwd` 만 칩니다.

   ① 한 단계 위 폴더로 이동합니다.

   ```bash
   cd ..
   ```

   - 하는 일: 한 단계 위 폴더로 이동합니다.
   - 나오는 것: 아무것도 나오지 않습니다.

   ② 지금 위치를 확인합니다.

   ```bash
   pwd
   ```

   - 하는 일: 지금 있는 폴더의 위치를 보여 줍니다.
   - 나오는 것: <mark style="background:#bde3ff">`…/security-agent-toolkit` 으로 끝나면</mark> 됩니다. 결과가 다르면 VS Code 왼쪽 목록에서 `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 새로 엽니다.

2. **[터미널]** 무엇이 바뀌었는지 먼저 봅니다. <mark style="background:#ffc4d6">빨간 글씨 줄이나 `Untracked files:` 아래에 `.env`(API 키가 들어 있는 파일) 나 `.venv`(가상환경이 들어 있는 폴더)가 보이면 올리지 말고(`.env` 를 올리면 키가 공개되기 때문입니다),</mark> 아래 안내대로 `.gitignore`(깃이 올리지 않을 파일 이름을 적어 두는 파일)를 고친 뒤 `git status` 를 다시 봅니다.

   ① 올릴 파일의 상태를 봅니다.

   ```bash
   git status
   ```

   - 하는 일: 올릴 파일의 상태를 보여 줍니다.
   - 나오는 것: 바뀐 파일의 이름이 나옵니다. `soar_response/` 아래의 새 파일들이 보이면 됩니다.

   - `.env` 가 보이면: VS Code 왼쪽 목록에서 `security-agent-toolkit` 바로 아래의 `.gitignore` 를 열어 맨 아래에 `.env` 한 줄을 적고 저장한 뒤 `git status` 를 다시 칩니다.
     - `.venv` 는 `.venv/` 한 줄을 같은 방법으로 적습니다.
   - `soar_response/__pycache__/` (파이썬이 실행하면서 자동으로 만드는 임시 폴더)가 보이면 `.gitignore` 맨 아래에 `__pycache__/` 한 줄을 적고 저장한 뒤 `git status` 를 다시 봅니다.

3. **[보고서]** `day05_pm_report.md` 의 `### 마무리 · 오늘 만든 것을 깃허브에 올리기` 아래를 채웁니다. <mark>올리기 전에 채워야</mark> 깃허브에 빈칸 없이 올라갑니다.
   - (가) `git status` 를 쳤을 때 `.env` 나 `.venv` 가 보였는지, 보였다면 어떻게 했는지 적어 주세요.
   - <mark>앞 교시에서 못 적은 보고서 칸이 있으면 `모름 — 막힌 곳: …` 으로 적고 올립니다.</mark> 올린 뒤에 이어서 적어 다시 올려도 됩니다.
4. **[터미널]** 바뀐 파일을 모두 올릴 목록에 추가하고(`add`), 기록하고(`commit`), 올립니다(`push`). 세 명령을 순서대로 하나씩 칩니다.

   ① 바뀐 파일을 모두 올릴 목록에 추가합니다.

   ```bash
   git add .
   ```

   - 하는 일: 바뀐 파일을 올릴 대상에 추가합니다.
   - 나오는 것: 아무것도 나오지 않습니다.

   ② 기록으로 저장합니다.

   ```bash
   git commit -m "Add incident report, approval gate, false positive recovery and risk assessment"
   ```

   - 하는 일: 따옴표 안의 설명을 붙여 기록으로 저장합니다.
   - 나오는 것: 바뀐 파일 수가 적힌 줄이 나옵니다.

   ③ 깃허브로 올립니다.

   ```bash
   git push
   ```

   - 하는 일: 저장한 기록을 깃허브로 올립니다.
   - 나오는 것: 올라간 내용이 몇 줄 나옵니다.

   - <mark style="background:#ffc4d6">`git push` 가 거절(`rejected`)되면 깃허브에 내 PC 에 없는 기록이 있다는 뜻입니다.</mark> `git pull --no-rebase`(깃허브의 새 기록을 내 PC 로 받아 와 합치는 명령)를 입력한 뒤 `git push` 를 다시 합니다.
   - 편집기 화면이 뜨면 `Esc` → `:wq`(저장하고 나가기) → `Enter` 를 합니다.
   - `git pull` 만 입력했을 때 `fatal: Need to specify how to reconcile divergent branches` 가 나오면, 내 기록과 깃허브 기록이 갈라졌다는 뜻이므로 `git pull --no-rebase` 를 입력합니다.

5. **[브라우저]** 깃허브의 내 저장소를 새로 고쳐 `soar_response` 폴더를 열고, VS Code 왼쪽 목록의 `soar_response` 폴더에 있는 파일들이 깃허브에도 보이는지 확인합니다. <mark>`__pycache__` 폴더는 없어도 됩니다</mark>.
   - 깃허브에 안 보이는 파일이 있으면, 그 파일이 VS Code 왼쪽 목록의 `soar_response` 폴더에 내 PC 에도 있는지 봅니다.
     - 없으면 다른 폴더에 만든 것이니 `soar_response` 안으로 이동하고, `pwd` 로 위치를 확인한 뒤 2번의 `git status` 부터 다시 합니다.

### 마무리 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 올릴 파일 확인 | `git status` (`.env` · `.venv` 가 보이면 멈춤) |
| 올리기 | `git add .` → `git commit -m "…"` → `git push` |
| 올린 뒤 | 브라우저에서 `soar_response` 폴더와 파일이 있는지 확인 |

---

## 오늘 오후 마무리

| 확인 | 문제 |
|---|---|
| 자동 조치마다 위험 점수 · 등급 · 빠진 통제(통제 갭)를 정리한 리스크 평가 문서를 작성했다 | 오후 5-1 |
| 평가 기준 세 가지를 자동 점검으로 한 번에 검증해 Day 4 점검 목록을 작성했다 | 오후 6-1 |
| 오늘 만든 파일과 보고서를 깃허브에 올렸다 | 마무리 |

**강의계획서 평가 기준 확인**

| 기준 | 확인할 곳 |
|---|---|
| 2 · 3일 차의 티켓 번호와 티켓 없는 조치의 인시던트 번호가 리포트에 들어 있다 | 오전 2교시 리포트의 1 · 5절, 오후 6교시 점검 ① |
| 위험 등급에 따라 자동 · 승인이 올바르게 나뉜다 | 오전 3교시 단계 2 · 3, 오후 6교시 점검 ② (시험 사례 7개) |
| 오탐 복구 절차가 신속하고 완전하게 처리된다 | 오전 4교시 단계 2 · 3 <mark style="background:#bde3ff">(25분 · 5분, 남은 대상 0개, `dami` 잠김)</mark>, 오후 6교시 점검 ③ |

리스크 평가 문서와 점검 목록은 한 번 작성하고 끝내지 않습니다. <mark>승인 기준이나 자동 조치가 바뀔 때마다 리스크 평가를 다시 수행하고, 점검 프로그램을 다시 실행해 「통과」가 유지되는지 확인합니다(회귀 시험).</mark> 통제를 보완한 뒤 남는 잔여 위험도 이때 다시 평가합니다. 다음 수업에서는 이번 주에 만든 것을 하나의 흐름으로 합칩니다.

---

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

아래 답은 한 예이고, <mark>핵심이 같으면 맞습니다.</mark> 줄 수가 달라도 주석이 말한 일을 하면 맞습니다.

---

### 정답 5-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day05_5-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예)

`risk_assessment.py` 의 1 ~ 7번입니다.

```python
    # 1. table["impact"] * table["likelihood"] 를 table["score"] 에 담는다 (위험 점수)
    table["score"] = table["impact"] * table["likelihood"]       # 두 열을 곱해 위험 점수 열을 만든다
    # 2. score 가 6 이상이면 (if, >=)
    if score >= 6:                                               # 6 이상이면
        # 3. "높음" 을 리턴한다
        return "높음"                                            # 높음을 리턴한다
        # 4. control 이 controls 안에 없으면 (if, not in)
        if control not in controls:                              # 지금 있는 통제에 없으면
            # 5. missing 에 control 을 추가한다 (append)
            missing.append(control)                              # 빠진 통제를 추가한다
    # 6. table.sort_values("score", ascending=False) 를 sorted_table 에 담는다 (점수가 큰 것부터)
    sorted_table = table.sort_values("score", ascending=False)   # 점수가 큰 행부터 정렬한다
        # 7. find_missing_controls(level, row["controls"]) 의 결과를 missing 에 담는다
        missing = find_missing_controls(level, row["controls"])  # 이 등급에 빠진 통제를 찾는다
```

`day05_5-1_run.py` 의 8 · 9번입니다.

```python
# 8. assess_risks(table) 의 결과를 rows 에 담는다
rows = assess_risks(table)         # 점수가 큰 것부터 등급과 빠진 통제를 붙인다
        # 9. gap_count 에 gap_count + 1 을 담는다 (1 늘린다)
        gap_count = gap_count + 1  # 빠진 통제가 있는 조치 수를 1 늘린다
```

**결과**

- (가) 출력은 다음과 같습니다. 높음은 <mark style="background:#bde3ff">**계정 잠금 · 세션 종료 · IP 차단**</mark>이고, 바로 보완할 조치는 <mark style="background:#bde3ff">**세션 종료(승인 게이트) · 담당자 알림(감사 기록)**</mark>입니다. 이 결과는 샘플의 통제 목록을 기준으로 산출한 검토 대상이므로, 실제 운영에서는 팀이 확인한 뒤 통제를 적용합니다.

```
--- 단계 1: 불러온 자동 조치 6 개
--- 단계 2: 점수가 큰 조치부터
계정 잠금 · 점수 6 · 높음 · 빠진 통제 []
세션 종료 · 점수 6 · 높음 · 빠진 통제 ['승인 게이트']
IP 차단 · 점수 6 · 높음 · 빠진 통제 []
담당자 알림 · 점수 3 · 보통 · 빠진 통제 ['감사 기록']
티켓 자동 작성 · 점수 2 · 낮음 · 빠진 통제 []
상급자 에스컬레이션 · 점수 2 · 낮음 · 빠진 통제 []
--- 단계 3: 바로 보완할 조치 2 개 · risk_assessment.md 16 줄 저장
```

리스크 평가 문서 `risk_assessment.md` 의 내용은 다음과 같습니다.

```
# 자동 대응 리스크 평가 — 2026-11-13(금)

- 점수 = 영향도(1~3) × 발생 가능성(1~3). 6 이상 높음, 3 이상 보통, 그 밖은 낮음

| 자동 조치 | 영향도 | 발생 가능성 | 점수 | 등급 | 지금 있는 통제 | 빠진 통제 |
|---|---|---|---|---|---|---|
| 계정 잠금 | 3 | 2 | 6 | 높음 | 승인 게이트, 되돌리기, 감사 기록, VIP 예외 | 없음 |
| 세션 종료 | 3 | 2 | 6 | 높음 | 감사 기록 | 승인 게이트 |
| IP 차단 | 3 | 2 | 6 | 높음 | 허용 목록, 승인 게이트, 자동 해제, 되돌리기, 감사 기록 | 없음 |
| 담당자 알림 | 1 | 3 | 3 | 보통 | 알림 간격, 재시도 | 감사 기록 |
| 티켓 자동 작성 | 1 | 2 | 2 | 낮음 | 병합, 감사 기록 | 없음 |
| 상급자 에스컬레이션 | 2 | 1 | 2 | 낮음 | 같은 단계 한 번 | 없음 |

## 바로 보완할 조치
- 세션 종료: 승인 게이트 추가
- 담당자 알림: 감사 기록 추가
```

- (나) 세 조치 모두 영향도 3 × 발생 가능성 2 = 6점으로 높음 등급이라, 필수 통제인 승인 게이트와 감사 기록이 있어야 합니다. 계정 잠금과 IP 차단의 `controls` 에는 둘 다 있지만, 세션 종료에는 <mark style="background:#bde3ff">`감사 기록`</mark> 하나뿐이라 <mark style="background:#ffc4d6">승인 게이트가 빠진 통제 갭이 생깁니다.</mark>
  - <mark style="background:#e0d4ff">수요일의 `rollback_incident`</mark> 는 세션 종료를 「되돌리기 불가」로 남깁니다. 잘못 실행된 뒤에는 교정 통제(되돌리기)를 쓸 수 없으니, <mark>실행하기 전에 막는 예방 통제인 승인 게이트</mark>가 더 중요합니다.
- (다) 점수는 영향도 1 × 발생 가능성 3 = <mark style="background:#bde3ff">3점</mark>이라 보통 등급입니다. 보통의 기준은 <mark style="background:#ffdcb0">3 이상 6 미만</mark>입니다. 피해(영향도)는 작아도 오탐 알림을 따로 제외하는 장치가 없다고 가정하므로 발생 가능성이 높기 때문입니다.
  - 탐지 통제인 감사 기록이 없으면 사고가 난 뒤 「어느 인시던트에 · 언제 · 어떤 알림을 보냈는지」를 확인할 수 없습니다. 받는 사람까지 알려면 기록에 따로 적어야 합니다. 담당자가 알림을 받았는데 응답하지 않았는지, 알림이 아예 가지 않았는지도 <mark style="background:#ffc4d6">가릴 수 없습니다.</mark>

**왜**

- <mark>리스크 평가는 「어떤 자동 조치가 위험한지」(위험 점수)와 「그 위험을 줄이는 통제가 갖춰져 있는지」(통제 갭 분석)를 한 표로 보여 줍니다.</mark> 점수가 같아도 통제가 다르면 보완할 내용이 달라지므로, 점수와 빠진 통제를 함께 적습니다.

**자주 틀리는 곳**

아래 결과는 해당 번호의 줄을 지우고 실행한 것입니다.

- 1번을 비워 두면 `score` 열이 없어서 6번의 정렬에서 오류가 납니다.

```
KeyError: 'score'
```

- 2번을 비워 두면 3번 줄이 바로 위 줄보다 오른쪽에서 시작해서(들여쓰기가 맞지 않아) 실행하기 전에 멈춥니다.

```
IndentationError: unexpected indent
```

- 2번에서 `>=` 대신 `>` 를 쓰면 오류 없이 <mark style="background:#ffc4d6">**점수 6인 조치가 모두 보통이 됩니다.**</mark> 점수가 기준값 6 과 같을 때 어긋나는 경계 조건 오류(off-by-one error)입니다. 세션 종료의 통제 갭이 사라지고, 보완할 조치가 1개로 줄어드는 것이 이 실수의 결과입니다.

```
계정 잠금 · 점수 6 · 보통 · 빠진 통제 []
세션 종료 · 점수 6 · 보통 · 빠진 통제 []
IP 차단 · 점수 6 · 보통 · 빠진 통제 []
--- 단계 3: 바로 보완할 조치 1 개 · risk_assessment.md 15 줄 저장
```

- 3번 · 5번을 비워 두면 `if` 아래에 실행할 줄이 없어 실행하기 전에 멈춥니다. 9번을 비워도 같은 오류가 납니다(문구는 파이썬 버전마다 조금 다릅니다).

```
IndentationError: expected an indented block
```

- 4번을 비워 두면 5번 줄이 `for` 바로 아래 줄이 되어 오류 없이 <mark style="background:#ffc4d6">**있어야 하는 통제가 모두 빠진 것으로 나옵니다.**</mark> 보완할 조치가 2개가 아니라 4개로 나오는 것이 이 실수의 결과입니다.

```
--- 단계 3: 바로 보완할 조치 4 개 · risk_assessment.md 18 줄 저장
```

- 6번을 비워 두면 `sorted_table` 이 만들어지지 않아 오류가 납니다. 7번 · 8번을 비워도 같은 꼴의 오류(`name 'missing'` · `name 'rows'`)가 납니다. 파이썬 버전에 따라 뒤에 `Did you mean: …` 이 더 붙을 수 있습니다.

```
NameError: name 'sorted_table' is not defined
```

- 6번에서 `ascending=False`(큰 값부터 정렬하라는 뜻)를 빠뜨리면 오류 없이 <mark style="background:#ffc4d6">**점수가 작은 조치부터 나옵니다.**</mark> 단계 2 의 첫 두 줄이 낮음으로 시작하는 것이 이 실수의 결과입니다.

```
티켓 자동 작성 · 점수 2 · 낮음 · 빠진 통제 []
상급자 에스컬레이션 · 점수 2 · 낮음 · 빠진 통제 []
```

**관제에서는**

- 보안 조직은 리스크 평가에서 영향도와 발생 가능성을 가로축과 세로축으로 놓고, 두 값이 만나는 곳마다 위험의 크기를 표시하는 표(**위험 매트릭스**, risk matrix, 리스크 매트릭스)를 자주 씁니다. 오늘은 같은 생각을 영향도 × 발생 가능성의 곱으로 단순하게 구현했습니다. <mark>자동 대응을 운영에 적용하기 전과 기준을 바꿀 때마다 다시 평가하고, 높음 등급 조치에는 승인 게이트(예방 통제) · 감사 기록(탐지 통제) 같은 통제를 두는 것이 일반적입니다.</mark> 통제를 적용한 뒤에도 남는 위험은 잔여 위험(residual risk)으로 따로 관리합니다. 오늘의 숫자 · 등급 기준 · 필요한 통제는 예시이고, 실제 값은 팀이 정합니다.

---

### 정답 6-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day05_6-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예)

`day4_check.py` 의 1 ~ 7번입니다.

```python
        # 1. number 가 report_text 안에 없으면 (if, not in)
        if number not in report_text:                             # 리포트에 그 번호가 없으면
            # 2. not_found 에 number 를 추가한다 (append)
            not_found.append(number)                              # 없는 번호를 추가한다
        # 3. decide_gate(case["request"], policy) 의 두 결과를 decision, reasons 에 담는다
        decision, reasons = decide_gate(case["request"], policy)  # 결정과 이유를 함께 받는다
        # 4. decision 이 case["expected"] 와 다르면 (if, !=)
        if decision != case["expected"]:                          # 기대한 결정과 다르면
        # 5. result["in_time"] 이 False 이면 (if not)
        if not result["in_time"]:                                 # 정한 시간 안에 끝나지 않았으면
        # 6. user 가 state["locked_users"] 안에 없으면 (if, not in)
        if user not in state["locked_users"]:                     # 진짜 공격 계정이 잠겨 있지 않으면
            # 7. problems 에 user + " 잠금이 풀림" 을 추가한다 (append)
            problems.append(user + " 잠금이 풀림")                # 문제를 추가한다
```

4 · 5번은 `if` 만 쓰고 `if` 안에 들어가는 줄은 미리 채운 줄이니, 완성된 모양을 함께 봅니다.

**전체 모양 — `check_gate`**

```python
def check_gate(cases, policy):                                    # 시험 사례 리스트와 승인 정책을 받는 함수
    """시험 사례마다 승인 게이트를 실행해, 결정이 기대한 결정과 다른 사례의 이름을 리스트로 리턴한다.
    승인 기준을 바꾼 뒤에도 자동 · 승인 필요 · 차단 금지가 맞게 나뉘는지 확인할 때 쓴다.
    """
    wrong = []                                                    # 기대와 다른 사례를 모을 빈 리스트 — 미리 채운 줄
    for case in cases:                                            # 시험 사례를 하나씩 꺼낸다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        decision, reasons = decide_gate(case["request"], policy)  # 결정과 이유를 함께 받는다
        if decision != case["expected"]:                          # 기대한 결정과 다르면
            wrong.append(case["case"] + " (기대 " + case["expected"] + ", 결과 " + decision + ")")  # 사례 이름과 두 결정을 추가한다 — 미리 채운 줄
    return wrong                                                  # 기대와 다른 사례 리스트를 리턴한다 — 미리 채운 줄
```

**전체 모양 — `check_recovery`**

```python
def check_recovery(results, state, true_positive_users):         # 오탐 처리 결과 · 처리 뒤 상태 · 진짜 공격 계정 리스트를 받는 함수
    """오탐 처리 결과에서 남은 대상 · 시간 초과를 찾고, 진짜 공격 계정이 풀렸는지도 확인해 문제 문장 리스트를 리턴한다.
    오탐 복구가 신속하고 완전했는지, 진짜 공격의 조치는 그대로인지 확인할 때 쓴다.
    """
    problems = []                                                # 문제 문장을 모을 빈 리스트 — 미리 채운 줄
    for result in results:                                       # 오탐 처리 결과를 하나씩 꺼낸다 — 미리 채운 줄
        if result["remaining"] != []:                            # 아직 복구되지 않은 대상이 있으면 — 미리 채운 줄
            problems.append(result["incident"] + " 복구 안 됨")  # 문제를 추가한다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        if not result["in_time"]:                                # 정한 시간 안에 끝나지 않았으면
            problems.append(result["incident"] + " 30분 넘음")   # 문제를 추가한다 — 미리 채운 줄
    for user in true_positive_users:                             # 진짜 공격 계정을 하나씩 꺼낸다 — 미리 채운 줄
        if user not in state["locked_users"]:                    # 진짜 공격 계정이 잠겨 있지 않으면
            problems.append(user + " 잠금이 풀림")               # 문제를 추가한다
    return problems                                              # 문제 문장 리스트를 리턴한다 — 미리 채운 줄
```

`day05_6-1_run.py` 의 8 · 9번입니다.

```python
# 8. check_report(report_text, tickets, actions) 의 결과를 report_problems 에 담는다
report_problems = check_report(report_text, tickets, actions)            # 리포트에 빠진 번호를 찾는다
# 9. check_recovery(results, state, TRUE_POSITIVE_USERS) 의 결과를 recovery_problems 에 담는다
recovery_problems = check_recovery(results, state, TRUE_POSITIVE_USERS)  # 오탐 복구의 문제를 찾는다
```

**결과**

- (가) 출력은 다음과 같습니다. 세 기준 모두 <mark style="background:#bde3ff">**통과**</mark>이고, `day4_checklist.md` 는 <mark style="background:#bde3ff">**5줄**</mark>입니다.

```
--- 단계 1: 점검 재료 · 티켓 7 장 · 조치 기록 10 건 · 시험 사례 7 개
--- 단계 2: Day 4 점검 목록
[통과] ① 2 · 3일 차 데이터가 리포트에 빠짐없이 들어갔다 · 문제 0 개
[통과] ② 위험 점수에 따라 자동 · 승인 필요 · 차단 금지가 맞게 나뉜다 · 문제 0 개
[통과] ③ 오탐 복구가 30분 안에 빠짐없이 끝났고 진짜 공격의 잠금은 그대로다 · 문제 0 개
--- 단계 3: day4_checklist.md 5 줄 저장
```

점검 목록 `day4_checklist.md` 의 내용은 다음과 같습니다.

```
# Day 4 마무리 점검 — 2026-11-13(금)

- [통과] ① 2 · 3일 차 데이터가 리포트에 빠짐없이 들어갔다
- [통과] ② 위험 점수에 따라 자동 · 승인 필요 · 차단 금지가 맞게 나뉜다
- [통과] ③ 오탐 복구가 30분 안에 빠짐없이 끝났고 진짜 공격의 잠금은 그대로다
```

- (나) 「대상 3개」는 등급 `mid`(중간)가 주는 1점만 있어 <mark style="background:#bde3ff">1점 · 자동</mark>이고, 「대상 4개」는 mid 1점 + 대상 수 2점으로 <mark style="background:#bde3ff">3점 · 승인 필요</mark>입니다.
  - <mark style="background:#ffdcb0">기준이 「3개 넘음(`>`)」</mark>인데 코드가 「3개 이상(`>=`)」으로 바뀌면(경계 조건 오류), 대상 3개 사례가 승인 필요로 바뀌어 <mark style="background:#ffc4d6">점검이 바로 「확인 필요」를 냅니다.</mark> 경계값의 양쪽(안쪽과 바깥쪽)을 함께 포함해야 이런 실수를 검출합니다.
- (다) <mark style="background:#e0d4ff">`rollback_incident`</mark> 가 신고된 인시던트가 아닌 기록까지 되돌리면 <mark style="background:#ffc4d6">정탐(진짜 공격)인 `dami` 의 잠금이 풀릴 수 있습니다.</mark> 남은 대상과 시간만 확인하면 오탐 복구가 「통과」로 보일 수 있으므로, 정탐 계정의 잠금이 그대로인지도 따로 확인해야 이 실수를 놓치지 않습니다.

**왜**

- <mark>자동 점검은 「기대한 결과」를 미리 적어 두고 실제 결과와 비교합니다.</mark> 기준 숫자나 코드를 바꾼 뒤 한 번 실행하면(회귀 시험), 사람이 출력을 다시 읽지 않아도 어디가 잘못됐는지 알 수 있습니다.

**자주 틀리는 곳**

아래 결과는 해당 번호의 줄을 지우고 실행한 것입니다.

- 1번을 비워 두면 2번 줄이 `for` 바로 아래 줄이 되어 오류 없이 <mark style="background:#ffc4d6">**있어야 할 번호가 모두 「없음」으로 나옵니다.**</mark> ① 이 「확인 필요 · 문제 8 개」로 나오는 것이 이 실수의 결과입니다(아래는 앞 세 줄).

```
[확인 필요] ① 2 · 3일 차 데이터가 리포트에 빠짐없이 들어갔다 · 문제 8 개
   - TCK-1
   - TCK-2
```

- 2번을 비워 두면 `if` 아래에 실행할 줄이 없어 실행하기 전에 멈춥니다. 7번을 비워도 같은 오류가 납니다(문구는 파이썬 버전마다 조금 다릅니다).

```
IndentationError: expected an indented block
```

- 3번을 비워 두면 `decision` 이 만들어지지 않아 오류가 납니다. 8번 · 9번을 비워도 같은 꼴의 오류(`name 'report_problems'` · `name 'recovery_problems'`)가 납니다. 파이썬 버전에 따라 뒤에 `Did you mean: …` 이 더 붙을 수 있습니다.

```
NameError: name 'decision' is not defined
```

- 4번을 비워 두면 미리 채운 `wrong.append(…)` 줄이 바로 위 줄보다 오른쪽에서 시작해서(들여쓰기가 맞지 않아) 실행하기 전에 멈춥니다.

```
IndentationError: unexpected indent
```

- 4번에서 `!=` 대신 `==` 를 쓰면 오류 없이 <mark style="background:#ffc4d6">**맞게 나온 사례가 모두 문제로 나옵니다.**</mark> ② 가 「확인 필요 · 문제 7 개」로 나오는 것이 이 실수의 결과입니다(아래는 앞 두 줄).

```
[확인 필요] ② 위험 점수에 따라 자동 · 승인 필요 · 차단 금지가 맞게 나뉜다 · 문제 7 개
   - high 등급 한 명 (기대 자동, 결과 자동)
```

- 5번을 비워 두면 오류는 나지 않고 출력도 정답과 같습니다. 아래 `problems.append(…)` 줄이 위 `if` 안으로 들어가서, <mark style="background:#ffc4d6">**30분을 넘긴 복구를 찾지 못합니다.**</mark> 오늘 샘플은 두 신고 모두 30분 안이라 차이가 보이지 않으니, 출력이 맞아도 코드를 다시 읽어 확인합니다.
- 6번을 비워 두면 7번 줄이 `for` 바로 아래 줄이 되어 오류 없이 <mark style="background:#ffc4d6">**잠겨 있는 `dami` 도 「잠금이 풀림」으로 나옵니다.**</mark>

```
[확인 필요] ③ 오탐 복구가 30분 안에 빠짐없이 끝났고 진짜 공격의 잠금은 그대로다 · 문제 1 개
   - dami 잠금이 풀림
```

**관제에서는**

- 대응 절차와 자동 대응 규칙은 바꿀 때마다 시험 사례를 다시 실행해(회귀 시험) 확인합니다. <mark>기대한 결과를 적은 시험 사례를 경계값까지 포함해 계속 추가해 두면, 기준을 바꾼 뒤 무엇이 달라졌는지 바로 알 수 있습니다.</mark> 오늘의 사례 7개와 점검 세 가지는 예시입니다.
