import pandas as pd

REPORT_TITLE = "# 초동 대응 리포트 — 2026-11-12(목) 오전 근무"


def make_ticket_table(tickets):
    table = pd.DataFrame(tickets)
    table["ack_minutes"] = table["acked_at"] - table["created_at"]
    return table


def count_by_rule(table):
    rule_counts = table["rule"].value_counts()
    return rule_counts.to_dict()


def mean_ack_by_grade(table):
    acked = table[table["acked_at"] >= 0]
    groups = acked.groupby("grade")
    grade_means = groups["ack_minutes"].mean()
    rounded = grade_means.round(1)
    return rounded.to_dict()


def find_late_tickets(table):
    late = table[table["acked_at"] > table["sla_due"]]
    return late.to_dict("records")


def find_missing_incidents(actions, tickets):
    covered = []
    for ticket in tickets:
        for incident_id in ticket["incidents"]:
            covered.append(incident_id)
    missing = []
    for action in actions:
        if action["incident"] not in covered:
            missing.append(action)
    return missing


def count_actions(ticket, actions):
    count = 0
    for action in actions:
        if action["incident"] in ticket["incidents"]:
            count = count + 1
    return count


def make_timeline_line(ticket):
    steps = [str(ticket["created_at"]) + "분 티켓 생성"]
    if ticket["acked_at"] >= 0:
        steps.append(str(ticket["acked_at"]) + "분 담당자 확인")
    if ticket["resolved_at"] >= 0:
        steps.append(str(ticket["resolved_at"]) + "분 해결")
    return "- " + ticket["id"] + " · " + ticket["entity"] + ": " + " → ".join(steps)


def make_report_lines(tickets, actions, rule_counts, grade_means, late_tickets, missing):
    lines = [REPORT_TITLE, ""]
    lines.append("## 1. 티켓별 초동 대응")
    for ticket in tickets:
        action_count = count_actions(ticket, actions)
        head = "- " + ticket["id"] + " [" + ticket["grade"] + "] " + ticket["entity"] + " — " + ticket["rule"]
        lines.append(head + " · 상태 " + ticket["status"] + " · 조치 기록 " + str(action_count) + "건")
    lines.append("")
    lines.append("## 2. 규칙별 티켓 수")
    for rule in rule_counts:
        count = rule_counts[rule]
        lines.append("- " + rule + ": " + str(count) + "장")
    lines.append("")
    lines.append("## 3. 등급별 평균 확인 시간(분)")
    for grade in grade_means:
        lines.append("- " + grade + ": " + str(grade_means[grade]) + "분")
    lines.append("")
    lines.append("## 4. 응답 기한을 넘겨 확인한 티켓")
    for ticket in late_tickets:
        lines.append("- " + ticket["id"] + " · 기한 " + str(ticket["sla_due"]) + "분 · 확인 " + str(ticket["acked_at"]) + "분")
    lines.append("")
    lines.append("## 5. 티켓이 없는 조치 (사람이 티켓을 만들어야 함)")
    for action in missing:
        lines.append("- " + action["incident"] + " · " + action["action"] + " · " + action["target"])
    lines.append("")
    lines.append("## 6. 높음(high) 티켓의 처리 경위")
    for ticket in tickets:
        if ticket["grade"] == "high":
            lines.append(make_timeline_line(ticket))
    return lines
