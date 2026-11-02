import json


def read_log(path):
    entries = []
    with open(path, encoding="utf-8") as log_file:
        for line in log_file:
            entry = json.loads(line)
            entries.append(entry)
    return entries


def count_by(entries, key):
    counts = {}
    for entry in entries:
        value = entry[key]
        old_count = counts.get(value, 0)
        counts[value] = old_count + 1
    return counts


def filter_denied(entries):
    denied = []
    for entry in entries:
        if not entry["allowed"]:
            denied.append(entry)
    return denied


def deny_rate(entries):
    total = len(entries)
    if total == 0:
        return 0.0
    denied = len(filter_denied(entries))
    return denied / total


def find_heavy_users(denied_counts, limit):
    heavy = []
    for user, count in denied_counts.items():
        if count >= limit:
            heavy.append(user)
    return heavy
