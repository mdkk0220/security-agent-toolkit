def average(numbers):
    if len(numbers) == 0:
        return 0
    return sum(numbers) / len(numbers)


def collect_response_times(tickets):
    times = []
    for ticket in tickets:
        if ticket["acked_at"] != -1:
            times.append(ticket["acked_at"] - ticket["created_at"])
    return times


def collect_resolve_times(tickets):
    times = []
    for ticket in tickets:
        if ticket["resolved_at"] != -1:
            times.append(ticket["resolved_at"] - ticket["created_at"])
    return times


def count_sla_breaches(tickets, now):
    late = 0
    for ticket in tickets:
        checked_time = ticket["acked_at"]
        if checked_time == -1:
            checked_time = now
        if checked_time > ticket["sla_due"]:
            late = late + 1
    return late
