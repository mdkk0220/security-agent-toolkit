import json
import sys
from pathlib import Path

import requests

RISK_PATH = Path(__file__).with_name("day03_risk_scores.json")
SUMMARY_LIMIT = 3
FAIL_TEXT = "(요약 실패 — 점수와 이유를 직접 확인)"
RULE_MEANING = {
    "퇴사한 계정": "퇴사한 사람의 계정으로 서버에 요청함",
    "권한 없음": "역할에 없는 권한을 서버에 요청함",
    "규칙은 허용인데 서버가 거절": "규칙으로는 허용되는 요청을 서버가 거절함",
    "업무 시간 밖 로그인": "업무 시간 밖에 SaaS에 로그인함",
    "평소와 다른 IP": "평소와 다른 IP에서 SaaS에 접속함",
    "대량 다운로드": "SaaS에서 파일을 한꺼번에 많이 내려받음",
    "경로 스캔": "없는 주소를 연달아 요청해 서버에 무엇이 있는지 확인함",
    "여러 로그 연결": "서로 다른 로그에서 한 사용자의 이벤트가 짧은 시간 안에 확인됨",
}
PROMPT_RULES = (
    "당신은 보안 관제 담당자를 돕는 도우미입니다. 아래 [사실]만 사용해 한국어 두 문장 이하로 요약하세요. "
    "[사실]에 없는 내용은 지어내지 말고, 공격이라고 단정하지 마세요. 점수와 등급은 우선 확인 순서이지 "
    "공격의 증거가 아닙니다. 제공된 사실에서 확인할 수 있는 것을 한 가지 제안하세요.\n"
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from agent_core_1.llm_client import call_llm


def load_records(path=RISK_PATH):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def pick_records_to_summarize(records):
    picked = []
    for record in records:
        if record["grade"] != "low" and len(picked) < SUMMARY_LIMIT:
            picked.append(record)
    return picked


def describe_reasons(reasons):
    meanings = [RULE_MEANING[rule] for rule in reasons]
    return "; ".join(meanings)


def build_prompt(record):
    facts = (
        f"[사실] 대상: {record['entity']} / 등급: {record['grade']} / "
        f"점수: {record['score']}점 / 탐지된 내용: {describe_reasons(record['reasons'])}"
    )
    return PROMPT_RULES + facts


def summarize_record(record):
    try:
        summary = call_llm(build_prompt(record)).strip()
    except requests.RequestException as error:
        print(f"[LLM 호출 실패] {type(error).__name__}: {error}")
        return FAIL_TEXT
    except (AttributeError, IndexError, KeyError, OSError, TypeError, ValueError) as error:
        print(f"[LLM 응답 처리 실패] {type(error).__name__}: {error}")
        return FAIL_TEXT
    return summary or FAIL_TEXT


def fallback_summary(record):
    reasons = ", ".join(record["reasons"])
    return (
        f"AI 호출 생략 — 대상 {record['entity']}: {record['score']}점 "
        f"({record['grade']}), 탐지 규칙: {reasons}."
    )


def summarize_records(records, offline=False):
    summaries = []
    for record in pick_records_to_summarize(records):
        if offline:
            status = "skipped"
            summary = fallback_summary(record)
        else:
            summary = summarize_record(record)
            status = "failed" if summary == FAIL_TEXT else "ok"
        summaries.append(
            {
                "entity": record["entity"],
                "status": status,
                "summary": summary,
            }
        )
    return summaries
