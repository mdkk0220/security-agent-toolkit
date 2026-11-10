def collect_failures(action_log):
    failures = []
    for entry in action_log:
        if entry["result"].startswith("실패"):
            failures.append(entry)
    return failures
