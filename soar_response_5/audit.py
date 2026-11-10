def log_line(item, action, text):
    entry = {
        "incident": item["id"],
        "playbook": item["playbook"],
        "action": action,
        "result": text,
    }
    return entry
