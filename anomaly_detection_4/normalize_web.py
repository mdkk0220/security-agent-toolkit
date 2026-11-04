from datetime import datetime
from log_parse import split_request, read_request, read_status, read_client

NGINX_TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"
COMMON_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def read_time_text(prefix):
    """Extract the bracketed timestamp from the request prefix."""
    parts = prefix.split()
    bracket_text = parts[3] + " " + parts[4]
    time_text = bracket_text.strip("[]")
    return time_text


def convert_time(time_text):
    """Convert an nginx timestamp to the common local-time format."""
    parsed = datetime.strptime(time_text, NGINX_TIME_FORMAT)
    local_time = parsed.replace(tzinfo=None)
    time_out = local_time.strftime(COMMON_TIME_FORMAT)
    return time_out


def convert_result(status):
    """Map HTTP status codes to the common success/failure labels."""
    if status >= 400:
        return "실패"
    return "성공"


def normalize_web(line):
    """Convert one web access-log line to a common event."""
    if line.count('"') < 2:
        return None
    prefix, request_text, suffix = split_request(line)
    method, path = read_request(request_text)
    status = read_status(suffix)
    client_ip = read_client(prefix)
    time_text = read_time_text(prefix)
    time_out = convert_time(time_text)
    result = convert_result(status)
    action = method + " " + path
    raw_text = line.strip()
    event = {
        "time": time_out,
        "source": "web",
        "user": None,
        "ip": client_ip,
        "action": action,
        "result": result,
        "raw": raw_text,
    }
    return event
