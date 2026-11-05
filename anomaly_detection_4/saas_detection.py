import pandas as pd

EVENTS_PATH = "normalized_events.json"
USUAL_IPS = {
    "seoyeon": "198.51.100.9",
    "junho": "192.0.2.41",
    "jiwoo": "198.51.100.52",
}
BUSINESS_START = 8
BUSINESS_END = 20
DOWNLOAD_LIMIT = 5


def load_events(path):
    """Load normalized events into a DataFrame."""
    return pd.read_json(path)


def pick_saas(events):
    """Select SaaS events."""
    is_saas = events["source"] == "saas"
    saas = events[is_saas]
    return saas


def pick_logins(saas):
    """Select login events."""
    is_login = saas["action"] == "login"
    logins = saas[is_login]
    return logins


def find_off_hours_logins(logins):
    """Select login attempts outside business hours."""
    times = pd.to_datetime(logins["time"])
    hours = times.dt.hour
    is_business_hour = hours.between(BUSINESS_START, BUSINESS_END)
    is_off_hours = ~is_business_hour
    off_hours_logins = logins[is_off_hours]
    return off_hours_logins


def find_new_ip_users(logins):
    """Return users logging in from an IP different from their known usual IP."""
    new_ip_users = []
    login_list = logins.to_dict("records")
    for login in login_list:
        user = login["user"]
        ip = login["ip"]
        usual_ip = USUAL_IPS.get(user)
        has_usual_ip = usual_ip is not None
        is_new_ip = ip != usual_ip
        if has_usual_ip and is_new_ip:
            new_ip_users.append(user)
    return new_ip_users


def find_bulk_download_users(saas):
    """Return users with at least DOWNLOAD_LIMIT file downloads."""
    actions = saas["action"]
    is_download = actions == "file.download"
    downloads = saas[is_download]
    counts = downloads.groupby("user").size()
    is_bulk = counts >= DOWNLOAD_LIMIT
    bulk_counts = counts[is_bulk]
    bulk_users = list(bulk_counts.index)
    return bulk_users
