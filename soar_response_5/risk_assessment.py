import pandas as pd

REQUIRED_CONTROLS = {
    "높음": ["승인 게이트", "감사 기록"],
    "보통": ["감사 기록"],
    "낮음": [],
}


def make_risk_table(risks):
    table = pd.DataFrame(risks)
    table["score"] = table["impact"] * table["likelihood"]
    return table


def risk_level(score):
    if score >= 6:
        return "높음"
    if score >= 3:
        return "보통"
    return "낮음"


def find_missing_controls(level, controls):
    missing = []
    required = REQUIRED_CONTROLS[level]
    for control in required:
        if control not in controls:
            missing.append(control)
    return missing


def assess_risks(table):
    sorted_table = table.sort_values("score", ascending=False, kind="stable")
    rows = []
    for row in sorted_table.to_dict("records"):
        level = risk_level(row["score"])
        missing = find_missing_controls(level, row["controls"])
        row["level"] = level
        row["missing"] = missing
        rows.append(row)
    return rows


def make_assessment_lines(rows):
    lines = ["# 자동 대응 리스크 평가 — 2026-11-13(금)", ""]
    lines.append("- 점수 = 영향도(1~3) × 발생 가능성(1~3). 6 이상 높음, 3 이상 보통, 그 밖은 낮음")
    lines.append("")
    lines.append("| 자동 조치 | 영향도 | 발생 가능성 | 점수 | 등급 | 지금 있는 통제 | 빠진 통제 |")
    lines.append("|---|---|---|---|---|---|---|")
    for row in rows:
        controls_text = ", ".join(row["controls"])
        missing_text = ", ".join(row["missing"])
        if missing_text == "":
            missing_text = "없음"
        numbers = str(row["impact"]) + " | " + str(row["likelihood"]) + " | " + str(row["score"])
        lines.append("| " + row["action"] + " | " + numbers + " | " + row["level"] + " | " + controls_text + " | " + missing_text + " |")
    lines.append("")
    lines.append("## 바로 보완할 조치")
    for row in rows:
        if row["missing"] != []:
            gap_text = ", ".join(row["missing"])
            lines.append("- " + row["action"] + ": " + gap_text + " 추가")
    return lines
