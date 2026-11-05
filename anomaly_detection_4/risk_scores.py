import json

import pandas as pd

from access_detection import (
    EVENTS_PATH,
    judge_failure,
    load_events,
    pick_server_failures,
    pick_suspicious,
)
from malicious_detection import find_scan_ips, pick_web_failures
from saas_detection import (
    find_bulk_download_users,
    find_new_ip_users,
    find_off_hours_logins,
    pick_logins,
    pick_saas,
)

RISK_PATH = "day03_risk_scores.json"
HIGH_LIMIT = 60
MID_LIMIT = 35
WEIGHTS = {
    "퇴사한 계정": 60,
    "권한 없음": 20,
    "규칙은 허용인데 서버가 거절": 10,
    "업무 시간 밖 로그인": 15,
    "평소와 다른 IP": 20,
    "대량 다운로드": 25,
    "경로 스캔": 30,
    "여러 로그 연결": 30,
}
SERVER_RULES = {
    "퇴사한 계정": "퇴사한 계정",
    "권한 없음": "권한 없음",
    "허용": "규칙은 허용인데 서버가 거절",
}


def add_finding(findings, entity, rule):
    finding = {"entity": entity, "rule": rule}
    if finding not in findings:
        findings.append(finding)


def collect_findings(events, chains):
    findings = []

    server_failures = pick_server_failures(events)
    suspicious = pick_suspicious(server_failures)
    for event in suspicious.to_dict("records"):
        reason, priority = judge_failure(event["user"], event["action"])
        rule = SERVER_RULES.get(reason, reason)
        add_finding(findings, event["user"], rule)

    saas = pick_saas(events)
    logins = pick_logins(saas)
    for user in find_off_hours_logins(logins)["user"]:
        add_finding(findings, user, "업무 시간 밖 로그인")
    for user in find_new_ip_users(logins):
        add_finding(findings, user, "평소와 다른 IP")
    for user in find_bulk_download_users(saas):
        add_finding(findings, user, "대량 다운로드")

    web_failures = pick_web_failures(events)
    scan_ips, scan_counts = find_scan_ips(web_failures)
    for ip in scan_ips:
        add_finding(findings, ip, "경로 스캔")

    for chain in chains:
        add_finding(findings, chain["user"], "여러 로그 연결")
    return findings


def score_findings(findings):
    findings_table = pd.DataFrame(findings)
    points = findings_table["rule"].map(WEIGHTS)
    findings_table["points"] = points
    grouped = findings_table.groupby("entity")
    totals = grouped["points"].sum()
    totals = totals.sort_values(ascending=False)
    return totals


def make_grade(score):
    if score >= HIGH_LIMIT:
        return "high"
    if score >= MID_LIMIT:
        return "mid"
    return "low"


def collect_reasons(findings):
    reasons = {}
    for finding in findings:
        entity = finding["entity"]
        if entity not in reasons:
            reasons[entity] = []
        reasons[entity].append(finding["rule"])
    return reasons


def make_records(totals, reasons):
    records = []
    for entity, score in totals.items():
        grade = make_grade(score)
        record = {
            "entity": entity,
            "score": int(score),
            "grade": grade,
            "reasons": reasons[entity],
        }
        records.append(record)
    return records


def save_records(records, path):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)
    return len(records)
