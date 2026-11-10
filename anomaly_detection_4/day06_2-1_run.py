import argparse
import sys

from event_summary import (
    RISK_PATH,
    SUMMARY_LIMIT,
    build_prompt,
    load_records,
    pick_records_to_summarize,
    summarize_records,
)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="점수 기록을 바탕으로 대상별 요약을 만듭니다.")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Gemini API를 호출하지 않고 대체 문장으로 로컬 검증합니다.",
    )
    args = parser.parse_args()

    records = load_records(RISK_PATH)
    picked = pick_records_to_summarize(records)
    print(f"--- 단계 1: 불러온 점수 기록 {len(records)} 건")
    print(f"--- 단계 2: 요약할 대상 {len(picked)} 명 (최대 {SUMMARY_LIMIT} 명)")
    for record in picked:
        print(f"{record['grade']} {record['entity']} {record['score']}")

    preview = next((record for record in picked if record["entity"] == "seoyeon"), None)
    if preview is None and picked:
        preview = picked[0]
    if preview is not None:
        print(f"--- 단계 3: AI에게 보내는 글 ({preview['entity']})")
        print(build_prompt(preview))

    print("--- 단계 4: Gemini API를 활용한 AI 요약")
    summaries = summarize_records(records, offline=args.offline)
    for item in summaries:
        print(f"{item['entity']} : {item['summary']}")
    failed_count = sum(item["status"] == "failed" for item in summaries)
    skipped_count = sum(item["status"] == "skipped" for item in summaries)
    print(f"(요약 실패 {failed_count}건 · 호출 생략 {skipped_count}건)")


if __name__ == "__main__":
    main()
