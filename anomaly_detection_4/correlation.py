import pandas as pd

from access_detection import EVENTS_PATH, load_events, pick_server_failures
from malicious_detection import pick_web_failures
from saas_detection import pick_logins, pick_saas

MIN_SOURCES = 2
WINDOW_MINUTES = 60


def make_ip_user_map(logins):
    ip_user = {}
    for login in logins.to_dict("records"):
        if login["result"] == "성공":
            ip_user[login["ip"]] = login["user"]
    return ip_user


def attach_user_to_web(web_failures, ip_user):
    known_web = web_failures[web_failures["ip"].isin(list(ip_user))].copy()
    users = known_web["ip"].map(ip_user)
    known_web["user"] = users
    return known_web


def build_timeline(server_part, saas_part, web_part):
    timeline = pd.concat([server_part, saas_part, web_part])
    timeline = timeline.sort_values(["user", "time"])
    times = pd.to_datetime(timeline["time"])
    timeline["minute_of_day"] = times.dt.hour * 60 + times.dt.minute
    return timeline


def find_chains(timeline):
    grouped = timeline.groupby("user")
    source_counts = grouped["source"].nunique()
    latest = grouped["minute_of_day"].max()
    earliest = grouped["minute_of_day"].min()
    spans = latest - earliest

    chains = []
    not_chained = []
    for user in source_counts.index:
        source_count = source_counts[user]
        span = spans[user]
        has_many_sources = source_count >= MIN_SOURCES
        is_close = span <= WINDOW_MINUTES
        if has_many_sources and is_close:
            reason = (
                "서로 다른 로그 "
                + str(source_count)
                + "종류 · "
                + str(span)
                + "분 안"
            )
            chains.append({"user": user, "reason": reason})
        if has_many_sources and not is_close:
            not_chained.append(
                {
                    "user": user,
                    "source_count": int(source_count),
                    "span_minutes": int(span),
                }
            )
    return chains, not_chained


def find_chains_in_events(events):
    server_part = pick_server_failures(events)
    saas_part = pick_saas(events)
    logins = pick_logins(saas_part)
    ip_user = make_ip_user_map(logins)
    web_part = attach_user_to_web(pick_web_failures(events), ip_user)
    timeline = build_timeline(server_part, saas_part, web_part)
    chains, not_chained = find_chains(timeline)
    return chains
