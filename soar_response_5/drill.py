from enrichment import enrich_incident
from routing import decide_route
from containment_store import make_record
from containment import contain_account
from ip_actions import check_ip_policy, block_ip, DEFAULT_TTL

CONTAINMENT_BY_RULE = {"퇴사한 계정": "계정 조치", "경로 스캔": "IP 차단"}
FIREWALL_DOWN_FOR = ["INC-005"]


def choose_containment(incident):
    for rule in incident["reasons"]:
        if rule in CONTAINMENT_BY_RULE:
            return CONTAINMENT_BY_RULE[rule]
    return "없음"


def handle_incident(incident, state, refs):
    enrich_incident(
        incident,
        refs["users_info"],
        refs["source_ips"],
        refs["trusted_ips"],
    )
    route, reason = decide_route(incident)
    if route == "오탐 종료":
        return "오탐 종료", []
    if route == "승인 필요":
        return "승인 대기", []
    kind = choose_containment(incident)
    entity = incident["entity"]
    if kind == "계정 조치":
        records = contain_account(
            entity,
            state,
            refs["vip_accounts"],
            incident["id"],
            incident["reasons"][0],
        )
        return "조치함", records
    if kind == "IP 차단":
        if incident["id"] in FIREWALL_DOWN_FOR:
            return "조치 실패", [
                make_record(
                    "IP 차단",
                    entity,
                    incident["id"],
                    "차단되지 않음",
                    "차단되지 않음 (확인 실패)",
                    "방화벽 연결 실패",
                )
            ]
        refusal = check_ip_policy(
            entity,
            refs["allowlist_ips"],
            refs["ip_users"],
        )
        if refusal != "":
            status = "조치하지 않음"
            if "승인 필요" in refusal:
                status = "승인 대기"
            return status, [
                make_record(
                    "IP 차단",
                    entity,
                    incident["id"],
                    "변경 없음",
                    "변경 없음",
                    refusal,
                )
            ]
        return "조치함", [
            block_ip(entity, state, incident["id"], incident["reasons"][0], DEFAULT_TTL)
        ]
    return "조치하지 않음", []
