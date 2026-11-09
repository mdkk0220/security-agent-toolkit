import json
from datetime import datetime

INCIDENTS_PATH = "incident_samples.json"
REGISTRY_PATH = "config/playbook_registry.json"
STATE_PATH = "system_state.json"
LOG_PATH = "action_log.json"
GRADE_ORDER = {"low": 1, "mid": 2, "high": 3}
TRANSITIONS = {
    "탐지됨": ["분류됨"],
    "분류됨": ["조치됨", "종료"],
    "조치됨": ["보고됨"],
    "보고됨": ["종료"],
    "종료": [],
}


def load_json(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def change_status(incident, new_status):
    allowed_statuses = TRANSITIONS[incident["status"]]
    if new_status not in allowed_statuses:
        return False
    incident["status"] = new_status
    return True


def is_grade_enough(incident_grade, min_grade):
    return GRADE_ORDER[incident_grade] >= GRADE_ORDER[min_grade]


def match_playbooks(incident, registry):
    matched = []
    for playbook in registry:
        has_rule = playbook["trigger_rule"] in incident["reasons"]
        grade_ok = is_grade_enough(incident["grade"], playbook["min_grade"])
        if has_rule and grade_ok:
            matched.append(playbook)
    return matched


def run_action(action, incident, state):
    entity = incident["entity"]
    is_ip = "." in entity
    if action == "계정 잠금":
        if is_ip:
            return "건너뜀: 대상이 IP 라서 계정 잠금을 할 수 없습니다"
        state["locked_users"].append(entity)
        return "계정 " + entity + " 잠금 완료"
    if action == "IP 차단":
        if not is_ip:
            return "건너뜀: 대상이 사용자라서 IP 차단을 할 수 없습니다"
        state["blocked_ips"].append(entity)
        return "IP " + entity + " 차단 완료"
    if action == "티켓 생성":
        ticket_id = "TCK-" + str(len(state["tickets"]) + 1)
        ticket = {"id": ticket_id, "incident": incident["id"], "target": entity}
        state["tickets"].append(ticket)
        return "티켓 " + ticket_id + " 생성"
    if action == "담당자 알림":
        message = "인시던트 " + incident["id"] + " 확인 요청"
        state["notifications"].append(message)
        return "담당자 알림 전송"
    return "알 수 없는 액션: " + action


def make_log_entry(incident, playbook, action, result):
    now_text = datetime.now().strftime("%H:%M:%S")
    return {
        "time": now_text,
        "incident": incident["id"],
        "playbook": playbook["id"],
        "action": action,
        "result": result,
    }
