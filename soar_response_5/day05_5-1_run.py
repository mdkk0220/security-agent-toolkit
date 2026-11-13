import sys

from incident import load_json
from risk_assessment import make_risk_table, assess_risks, make_assessment_lines

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DOC_PATH = "risk_assessment.md"

risks = load_json("config/automation_risks.json")
print("--- 단계 1: 불러온 자동 조치", len(risks), "개")

table = make_risk_table(risks)
rows = assess_risks(table)
print("--- 단계 2: 점수가 큰 조치부터")
gap_count = 0
for row in rows:
    print(row["action"], "· 점수", row["score"], "·", row["level"], "· 빠진 통제", row["missing"])
    if row["missing"] != []:
        gap_count = gap_count + 1

lines = make_assessment_lines(rows)
text = "\n".join(lines) + "\n"
with open(DOC_PATH, "w", encoding="utf-8") as doc_file:
    doc_file.write(text)
print("--- 단계 3: 바로 보완할 조치", gap_count, "개 ·", DOC_PATH, len(lines), "줄 저장")
