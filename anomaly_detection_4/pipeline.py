import argparse
import json
import sys
from pathlib import Path

import requests

from access_detection import EVENTS_PATH, load_events
from correlation import find_chains_in_events
from risk_scores import (
    collect_findings,
    collect_reasons,
    make_records,
    score_findings,
)

REPORT_PATH = Path("day06_report.json")


def make_prompt(record):
    facts = {
        "entity": record["entity"],
        "score": record["score"],
        "grade": record["grade"],
        "reasons": record["reasons"],
    }
    return (
        "다음 JSON에 있는 사실만 사용해 한국어로 한두 문장 요약하세요.\n"
        "JSON에 없는 사실이나 원인을 만들어내지 마세요. 공격·침해라고 단정하거나 "
        "차단·계정 정지 같은 조치를 지시하지 마세요. 점수와 등급은 우선 확인 순서이며 "
        "공격의 증거가 아니라고 밝혀 주세요.\n"
        f"{json.dumps(facts, ensure_ascii=False)}"
    )


def fallback_summary(record, reason="AI 요약 실패"):
    reasons = ", ".join(record["reasons"])
    return (
        f"{reason} — {record['entity']}는 {record['score']}점 "
        f"({record['grade']})이며, 탐지 규칙은 {reasons}입니다."
    )


def summarize_record(record, offline):
    if offline:
        return {
            "entity": record["entity"],
            "status": "skipped",
            "summary": fallback_summary(record, "AI 호출 생략"),
        }

    repository_root = Path(__file__).resolve().parents[1]
    if str(repository_root) not in sys.path:
        sys.path.insert(0, str(repository_root))
    from agent_core_1.llm_client import call_llm, read_api_key

    try:
        api_key = read_api_key()
    except (IndexError, OSError, TypeError) as error:
        print(f"[LLM 호출 실패] API 키 설정을 읽지 못했습니다: {error}")
        return {
            "entity": record["entity"],
            "status": "failed",
            "summary": fallback_summary(record),
        }

    if not api_key:
        print("[LLM 호출 실패] GEMINI_API_KEY를 찾지 못했습니다.")
        return {
            "entity": record["entity"],
            "status": "failed",
            "summary": fallback_summary(record),
        }

    try:
        summary = call_llm(make_prompt(record)).strip()
    except requests.RequestException as error:
        print(f"[LLM 호출 실패] {type(error).__name__}: {error}")
        summary = ""
    except (IndexError, KeyError, TypeError, ValueError) as error:
        print(f"[LLM 응답 처리 실패] {type(error).__name__}: {error}")
        summary = ""

    if not summary:
        return {
            "entity": record["entity"],
            "status": "failed",
            "summary": fallback_summary(record),
        }
    return {"entity": record["entity"], "status": "ok", "summary": summary}


def run_pipeline(offline=False):
    events = load_events(EVENTS_PATH)
    chains = find_chains_in_events(events)
    findings = collect_findings(events, chains)
    totals = score_findings(findings)
    records = make_records(totals, collect_reasons(findings))
    summaries = [summarize_record(record, offline) for record in records]
    report = {
        "event_count": len(events),
        "finding_count": len(findings),
        "records": records,
        "summaries": summaries,
    }

    with REPORT_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    failed_count = sum(summary["status"] == "failed" for summary in summaries)
    skipped_count = sum(summary["status"] == "skipped" for summary in summaries)
    print(f"이벤트 {report['event_count']}개 · 탐지 규칙 {report['finding_count']}건")
    print(f"대상 기록 {len(records)}건 · 요약 {len(summaries)}건")
    print(f"요약 실패 {failed_count}건 · 호출 생략 {skipped_count}건")
    print(f"{REPORT_PATH} 저장")
    return report


def main():
    parser = argparse.ArgumentParser(description="탐지부터 위험 요약까지 실행합니다.")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Gemini API를 호출하지 않고 대체 문장으로 로컬 검증합니다.",
    )
    args = parser.parse_args()
    run_pipeline(offline=args.offline)


if __name__ == "__main__":
    main()
