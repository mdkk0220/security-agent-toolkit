def is_failure(record):
    return "확인 실패" in record["after"]


def is_unchanged(record):
    return record["before"] == record["after"]


def classify_record(record):
    if is_failure(record):
        return "확인 실패"
    if is_unchanged(record):
        return "변경 없음"
    return "변경됨"


def summarize(log):
    counts = {"변경됨": 0, "변경 없음": 0, "확인 실패": 0}
    for record in log:
        kind = classify_record(record)
        counts[kind] = counts[kind] + 1
    return counts
