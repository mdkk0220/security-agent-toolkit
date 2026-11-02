# 🛡️ security-agent-toolkit

![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/LLM-Gemini-4285F4?logo=googlegemini&logoColor=white)
![Flask](https://img.shields.io/badge/Webhook-Flask-000000?logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Lab-Docker-2496ED?logo=docker&logoColor=white)

**교육과정 실습으로 만든 보안 관제 자동화 에이전트와, 함께 공부한 네트워크 · 접근통제 · 이상탐지 실습을 모은 저장소입니다.**

> 핵심 원칙: **LLM은 고르기만 하고, 실행은 코드가 하고, 되돌리기 어려운 결정은 사람이 합니다.**

---

## 📂 구성

폴더 이름 끝의 숫자는 과목 순서입니다.

| 폴더 | 과목 | 내용 | 바로 가기 |
|---|---|---|---|
| **`agent_core_1/`** | 1과목 | ⭐ 메인 프로젝트. 로그 수집부터 보고서 · 알림까지 이어지는 보안 관제 자동화 파이프라인 | [자세히 보기](agent_core_1/README.md) |
| `network_zt_2/` | 2과목 | 네트워크 기초부터 제로트러스트 · 이슈 판정까지 일차별 학습 기록과 실습 코드 | [목차](#-network_zt_2--네트워크--제로트러스트) |
| `access_control_3/` | 3과목 | 역할 기반 접근통제(RBAC) → 예외 · 회수 · 조건기반 정책 → 주간 보고서 | [목차](#-access_control_3--접근통제) |
| `anomaly_detection_4/` | 4과목 | 접속 로그 읽기 · 이상 징후 가르기 · SIEM (진행 중) | [목차](#-anomaly_detection_4--이상탐지) |
| `docs/` | — | 날짜별 정리 노트와 회고 | [폴더](docs/) |

---

## ⭐ agent_core_1 — 보안 관제 자동화 에이전트

로그 수집 → 정규화 → 룰 탐지 → LLM 요약 · 판단 → 도구 실행 → 사람 승인 → 보고서 · 알림까지, 보안 관제의 한 사이클을 파이썬으로 구현한 과정 실습입니다. (제공받은 부분과 직접 한 부분은 [agent_core_1/README.md](agent_core_1/README.md)에 구분해 적었습니다.)

```mermaid
flowchart LR
    A[원본 로그] --> B[정규식 정규화]
    B --> C[룰 기반 탐지<br/>경보 생성]
    C --> D[LLM 요약 · 위험도 판정]
    D --> E[도구 호출 라우터<br/>조회 · 계정 잠금]
    E --> F{승인 게이트<br/>위험한 조치?}
    F -- 사람 승인 --> G[실행]
    F -- 그 외 --> H[보류 · held]
    D --> I[위험도순 일일 보고서]
    I --> J[웹훅 알림]
```

### 설계에서 신경 쓴 점

| 원칙 | 구현 |
|---|---|
| **사실은 코드가 확인한다** | 로그인 실패 횟수, IP 정보 같은 사실은 도구와 코드가 세고, LLM이 지어낸 값은 쓰지 않습니다 |
| **LLM의 답을 검증한다** | JSON이 아닌 답은 버리고 계속 진행합니다. 목록에 없는 도구 이름은 실행하지 않습니다 |
| **위험한 조치는 사람이 승인한다** | 계정 잠금은 담당자가 승인할 때만 실행하고, 아니면 `held`로 기록합니다 |
| **모르면 막는 쪽으로** | 처음 보는 위험도 값은 high로 보고 사람에게 묻습니다 |
| **일부가 실패해도 전체는 계속된다** | 알림 전송이 실패해도 보고서는 저장되고, 실패는 숨기지 않고 출력합니다 |
| **비밀은 코드에 두지 않는다** | API 키는 `.env`에만 두고 저장소에 올리지 않습니다 |

### 빠른 시작

```bash
git clone https://github.com/mdkk0220/security-agent-toolkit.git
cd security-agent-toolkit/agent_core_1
pip install requests flask
```

`agent_core_1/.env` 파일에 Gemini API 키를 넣습니다. (커밋하지 않습니다)
```
GEMINI_API_KEY=발급받은_키
```

```bash
python alert_server.py      # 터미널 1: 알림을 받는 웹훅 서버
python pipeline.py          # 터미널 2: 보고서 생성 + 알림 전송
python test_agent_core.py   # 단위 테스트
```

설정, 출력 예시, 모듈 구조, 개발 과정은 **[agent_core_1/README.md](agent_core_1/README.md)**에 있습니다.

---

## 🌐 network_zt_2 — 네트워크 · 제로트러스트

| 일차 | 주제 | 주요 파일 |
|---|---|---|
| Day 1 (10/12) | OSI 7계층 · TCP와 Wireshark 패킷 분석 | `day01_packet_analysis.md` · `261012_am_osi_layers.md` · `261012_pm_tcp_wireshark.md` |
| Day 2 (10/13) | IP · 서브넷 설계 · 스위치 · 라우터 · VLAN | `day02_subnet_design.md` · `261013_am_ip_subnet.md` · `261013_pm_switch_router_vlan.md` |
| Day 3 | DNS · 수상한 도메인(DGA) 탐지 | `day03_am_dns.md` · `day03_pm_dns_suspicious.md` · `day03_*.py` |
| Day 4 | VPN · 방화벽 | `day04_am_vpn.md` · `day04_pm_firewall.md` |
| Day 5 | 클라우드 구성도 · 서비스 품질 | `day05_am_cloud_diagram.md` · `day05_pm_quality.md` |
| Day 6 | 제로트러스트 · 접근 판정 점수 · Docker 기초 | `day06_am_zero_trust.md` · `day06_4-1_zt_score.py` · `day06_zt_scenario.md` · `day06_pm_docker_basics.md` |
| Day 7 | 정책 로그 · 규칙 튜닝 · Docker Compose | `day07_am_policy_log.md` · `day07_4-1_rule_tuning.py` · `day07_customer_report.md` · `day07_docker/` |
| Day 8 (10/21) | 서버 알림 판정 · 거부 직후 허용 탐지 · 이슈 도식 · 회고 | `day08_am_issue_map.md` · `day08_3-1_deny_then_allow.py` · `day08_issue_diagram.md` · `day08_retrospective.md` |

`warmup_*.py` · `ping_check.py` · `addr_kind.py`는 수업 시작 전 몸풀기 코드입니다.

---

## 🔐 access_control_3 — 접근통제

A사 계정 · 자원을 예로, 권한 판정부터 회수 · 주간 보고까지 접근통제의 한 주기를 단계별로 만들었습니다. 앞 단계 파일은 고치지 않고 새 파일로 쌓아 갔습니다.

| 일차 | 주제 | 주요 파일 |
|---|---|---|
| Day 1 (10/21) | 인증과 인가 · RBAC 권한 판정 · 기록으로 권한 점검 | `rbac.py` · `access_log.py` · `day01_7-1_audit.py` · `config/users.json` · `config/roles.json` |
| Day 2 (10/22) | 역할 부여 · 회수 · 기간이 정해진 예외 권한 · 설정이 고장 나도 거부 · 테스트 케이스 | `policy.py` · `exception_policy.py` · `config_loader.py` · `config/exceptions.json` · `day02_pm_tests.md` |
| Day 3 (10/23) | 권한 요청서 · 승인과 반려 · 정책 확인 후 부여 | `day03_am_request.md` |
| Day 4 (10/29) | 접근 점검 · 필요 없어진 권한 찾기 · 과다권한 리포트 · 회수 제외 | `review_list.py` · `review_rules.py` · `review_unused.py` · `overprivilege.py` · `report_exclude.py` |
| Day 5 (10/30) | 권한 회수 계획 · 승인 · 실행 · 이력 · 조건기반 정책 · 판정 서버 | `revoke_plan.py` · `revoke_approve.py` · `revoke.py` · `conditional.py` · `access_server.py` |
| Day 6 (11/2) | 점검 체크리스트 · 로그 집계 · 주간 보고서 | `checklist.py` · `log_summary.py` · `weekly_report.py` · `access_control_weekly_report_2026-11-02.md` |

설계에서 반복해 지킨 원칙:
- **목록에 없으면 거부**: 역할 권한 → 유효한 예외 → 거부 순서로 판정합니다
- **설정이 고장 나도 거부**: 설정 파일이 없거나 깨지면 경고를 내고 기본값(거부)으로 동작합니다
- **회수는 계획 → 승인 → 실행 → 이력** 순서로, 바로 지우지 않습니다

사용자 · 권한 데이터는 모두 실습용 가상 데이터입니다.

---

## 📈 anomaly_detection_4 — 이상탐지

| 일차 | 주제 | 주요 파일 |
|---|---|---|
| Day 1 (11/2) | 접속 로그 한 줄을 조각으로 읽기 · 이상 징후 가르기 · SIEM | `day01_pm_log_basics.md` |

---

## 📝 참고

- `*_report.md` 파일(`access_control_3/` 10개, `network_zt_2/` 11개, `anomaly_detection_4/` 1개)은 교시별 리포트입니다. 질문은 수업에서 주어졌고, `답:` 뒤의 내용은 직접 쓴 것입니다.
- 실습 문서 속 이름 · 주소 · 비밀번호 값은 모두 수업용 예시입니다.
- 무료 Gemini 키는 호출 횟수 제한이 있어, `429` 오류가 나면 1분 뒤 다시 실행하세요.
