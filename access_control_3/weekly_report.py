from log_summary import count_by, deny_rate, filter_denied, find_heavy_users


def build_report(results, entries, alert, today):
    denied = filter_denied(entries)
    total = len(entries)
    denied_count = len(denied)
    allowed_count = total - denied_count
    rate = deny_rate(entries)
    percent = round(rate * 100)
    limit = alert["deny_rate_limit"]
    limit_percent = round(limit * 100)
    status = "경고" if rate >= limit else "경고 없음"
    user_limit = alert["user_denied_limit"]
    user_counts = count_by(denied, "user")
    heavy = find_heavy_users(user_counts, user_limit)

    lines = [f"# 접근통제 주간 보고서 ({today})", ""]
    lines.append("## 1. 요청 현황")
    lines.append(
        f"- 전체 요청: {total}건 (허용 {allowed_count}건 · 거부 {denied_count}건)"
    )
    lines.append(f"- 거부율: {percent}% (경고 기준 {limit_percent}%) -> {status}")
    lines.append("")
    lines.append("## 2. 거부 사유")
    reason_counts = count_by(denied, "reason")
    for reason, count in reason_counts.items():
        lines.append(f"- {reason}: {count}건")
    lines.append("")
    lines.append("## 3. 점검 결과")
    for result in results:
        name = result["name"]
        problems = result["problems"]
        if len(problems) == 0:
            lines.append(f"- {name}: 통과")
        else:
            lines.append(f"- {name}: 실패 {problems}")
    lines.append("")
    lines.append("## 4. 조치가 필요한 것")
    lines.append(f"- 거부 {user_limit}번 이상 사용자: {heavy}")
    for result in results:
        name = result["name"]
        problems = result["problems"]
        if len(problems) > 0:
            lines.append(f"- 확인: {name} -> {problems}")
    return "\n".join(lines) + "\n"


def save_report(text, today):
    file_name = f"access_control_weekly_report_{today}.md"
    with open(file_name, "w", encoding="utf-8") as report_file:
        report_file.write(text)
    return file_name
