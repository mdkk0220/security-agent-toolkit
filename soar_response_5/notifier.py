import json

import requests

REQUIRED = ["model", "approve_severity", "report_folder", "webhook_url"]
RANK = {"low": 1, "medium": 2, "high": 3}


def load_config(path):
    with open(path, encoding="utf-8") as file:
        config = json.load(file)
    for key in REQUIRED:
        if key not in config:
            print("[설정 오류] 빠진 키:", key)
            return None
    return config


def needs_approval(severity, config):
    level = RANK.get(severity.lower(), 3)
    return level >= RANK[config["approve_severity"]]


def notify(message, url):
    try:
        requests.post(url, json={"text": message}, timeout=5)
        return True
    except Exception as e:
        print("[알림 실패]", type(e).__name__)
        return False
