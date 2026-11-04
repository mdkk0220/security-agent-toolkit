def split_request(line):
    """Split one access-log line into its prefix, request, and suffix."""
    prefix, request_text, suffix = line.split('"', 2)
    return prefix, request_text, suffix


def read_request(request_text):
    """Return the method and path from a request field."""
    method, path, protocol = request_text.split()
    return method, path


def read_status(suffix):
    """Return the HTTP status code as an integer."""
    parts = suffix.split()
    status_text = parts[0]
    status = int(status_text)
    return status


def read_client(prefix):
    """Return the client IP address from a log prefix."""
    parts = prefix.split()
    client_ip = parts[0]
    return client_ip


def parse_line(line):
    """Parse an access-log line or return None for a malformed line."""
    if line.count('"') < 2:
        return None
    prefix, request_text, suffix = split_request(line)
    method, path = read_request(request_text)
    status = read_status(suffix)
    client_ip = read_client(prefix)
    entry = {
        "ip": client_ip,
        "method": method,
        "path": path,
        "status": status,
    }
    return entry
