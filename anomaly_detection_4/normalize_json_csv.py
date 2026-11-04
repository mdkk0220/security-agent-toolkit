import csv
import json
from datetime import datetime

SERVER_TIME_FORMAT = "%Y-%m-%dT%H:%M"
COMMON_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
ALLOWED_MAP = {True: "성공", False: "실패"}
RESULT_MAP = {"success": "성공", "failure": "실패"}


def convert_server_time(time_text):
    """Convert a server timestamp to the common timestamp format."""
    parsed = datetime.strptime(time_text, SERVER_TIME_FORMAT)
    time_out = parsed.strftime(COMMON_TIME_FORMAT)
    return time_out


def normalize_server(line):
    """Convert one JSON decision-server log line to a common event."""
    item = json.loads(line)
    time_out = convert_server_time(item["time"])
    allowed = item["allowed"]
    result = ALLOWED_MAP[allowed]
    raw_text = line.strip()
    event = {
        "time": time_out,
        "source": "server",
        "user": item["user"],
        "ip": None,
        "action": item["permission"],
        "result": result,
        "raw": raw_text,
    }
    return event


def normalize_saas(row):
    """Convert one SaaS CSV row to a common event."""
    account_parts = row["account"].split("@")
    user = account_parts[0]
    outcome = row["outcome"]
    result = RESULT_MAP[outcome]
    event = {
        "time": row["time"],
        "source": "saas",
        "user": user,
        "ip": row["ip_address"],
        "action": row["event"],
        "result": result,
        "raw": row,
    }
    return event


def load_server(path):
    """Load and normalize all decision-server log lines."""
    events = []
    with open(path, encoding="utf-8") as server_file:
        for line in server_file:
            event = normalize_server(line)
            events.append(event)
    return events


def load_saas(path):
    """Load and normalize all SaaS CSV rows."""
    events = []
    with open(path, encoding="utf-8", newline="") as saas_file:
        reader = csv.DictReader(saas_file)
        for row in reader:
            event = normalize_saas(row)
            events.append(event)
    return events
