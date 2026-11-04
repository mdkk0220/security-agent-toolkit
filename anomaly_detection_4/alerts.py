import json

ALERTS_PATH = "alerts.json"


def make_alert(alert_type, target, count, note):
    """Create one alert with a consistent set of fields."""
    alert = {
        "type": alert_type,
        "target": target,
        "count": count,
        "note": note,
        "status": "확인 필요",
    }
    return alert


def make_login_alerts(alert_ips):
    """Create an alert for each IP address over the login failure limit."""
    alerts = []
    for ip_address, count in alert_ips.items():
        note = "로그인 실패가 기준 이상 — 공격 확정이 아니라 먼저 살펴볼 곳"
        alert = make_alert("비정상 로그인", ip_address, count, note)
        alerts.append(alert)
    return alerts


def make_traffic_alerts(spike_minutes):
    """Create an alert for each minute over the traffic spike limit."""
    alerts = []
    for minute, count in spike_minutes.items():
        note = "요청이 평소의 3배 이상으로 늘어남 — 공격 확정이 아니라 먼저 살펴볼 곳"
        target = str(minute)
        alert = make_alert("트래픽 급증", target, count, note)
        alerts.append(alert)
    return alerts


def save_alerts(alerts, path):
    """Write alerts to JSON and return the number saved."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(alerts, file, ensure_ascii=False, indent=2)
    saved_count = len(alerts)
    return saved_count
