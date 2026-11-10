import argparse
import json
from pathlib import Path

from access_detection import EVENTS_PATH, load_events
from correlation import find_chains_in_events
from event_summary import summarize_records
from risk_scores import (
    collect_findings,
    collect_reasons,
    make_records,
    score_findings,
)

REPORT_PATH = Path("day06_report.json")


def run_pipeline(offline=False):
    events = load_events(EVENTS_PATH)
    chains = find_chains_in_events(events)
    findings = collect_findings(events, chains)
    totals = score_findings(findings)
    records = make_records(totals, collect_reasons(findings))
    summaries = summarize_records(records, offline=offline)
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
