import pandas as pd

EVENTS_PATH = "normalized_events.json"
SCANNER_PATTERN = "/.env|/wp-login|/phpmyadmin"


def load_events(path):
    """Load normalized events into a DataFrame."""
    return pd.read_json(path)


def pick_web_failures(events):
    """Select failed events from the web server."""
    is_web = events["source"] == "web"
    is_fail = events["result"] == "실패"
    both_true = is_web & is_fail
    web_failures = events[both_true]
    return web_failures


def find_scan_ips(web_failures):
    """Find IP addresses that requested known scanner paths and their counts."""
    actions = web_failures["action"]
    is_scanner = actions.str.contains(SCANNER_PATTERN)
    scanner_rows = web_failures[is_scanner]
    scan_counts = scanner_rows["ip"].value_counts()
    scan_ips = list(scan_counts.index)
    return scan_ips, scan_counts


def explain_scan(ip, request_count):
    """Build a human-readable explanation for a suspected scan IP."""
    reason = "스캐너 경로를 " + str(request_count) + "번 요청"
    scan_info = {"ip": ip, "reason": reason}
    return scan_info
