from incident import change_status

IP_RELATED_RULES = ["평소와 다른 IP", "업무 시간 밖 로그인"]


def is_only_ip_related(incident):
    for rule in incident["reasons"]:
        if rule not in IP_RELATED_RULES:
            return False
    return True


def decide_route(incident):
    context = incident["context"]
    if context["vip"]:
        return "승인 필요", "VIP 계정이라 담당자 승인이 필요함"
    if context["ip_trusted"] and is_only_ip_related(incident):
        return "오탐 종료", "신뢰 IP에서 온 IP 관련 규칙뿐이라 정상 접속으로 봄"
    return "기본", "플레이북 기본 절차대로 처리함"


def apply_route(incident, route, reason, incident_log):
    if route == "오탐 종료":
        change_status(incident, "분류됨")
        change_status(incident, "종료")
    entry = {"incident": incident["id"], "route": route, "reason": reason}
    incident_log.append(entry)
