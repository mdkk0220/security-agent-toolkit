import ipaddress

RULES = [
    (1, "10.8.0.0/24", "10.10.20.5/32", 443, "허용"),
    (2, "10.8.0.0/24", "10.10.20.6/32", 443, "허용"),
    (3, "192.168.20.0/24", "10.10.20.5/32", 443, "허용"),
    (4, "192.168.20.0/24", "10.10.20.6/32", 443, "허용"),
    (5, "10.10.20.5/32", "10.10.30.7/32", 3306, "허용"),
    (6, "10.10.40.10/32", "10.10.20.9/32", 22, "허용"),
    (7, "10.8.0.50/32", "10.10.20.9/32", 22, "허용"),
    (8, "0.0.0.0/0", "0.0.0.0/0", "any", "차단"),
]

TESTS = [
    ("10.8.0.21", "10.10.20.5", 443, "허용"),
    ("10.8.0.21", "10.10.20.6", 443, "허용"),
    ("10.8.0.21", "10.10.30.7", 3306, "차단"),
    ("192.168.20.15", "10.10.20.5", 443, "허용"),
    ("192.168.20.15", "10.10.20.9", 443, "차단"),
    ("10.10.20.5", "10.10.30.7", 3306, "허용"),
    ("10.10.40.10", "10.10.20.9", 22, "허용"),
    ("211.36.10.7", "10.10.20.5", 443, "차단"),
    ("10.8.0.50", "10.10.20.9", 22, "허용"),
    ("10.8.0.21", "10.10.20.9", 22, "차단"),
]

score = 0
for src, dst, port, expected in TESTS:
    result = "맞는 규칙 없음"
    for _, rule_src, rule_dst, rule_port, action in RULES:
        src_ok = ipaddress.ip_address(src) in ipaddress.ip_network(rule_src)
        dst_ok = ipaddress.ip_address(dst) in ipaddress.ip_network(rule_dst)
        port_ok = rule_port == "any" or rule_port == port
        if src_ok and dst_ok and port_ok:
            result = action
            break
    if result == expected:
        score += 1
        print("맞음", src, "→", dst, port, ":", result)
    else:
        print("틀림", src, "→", dst, port, ":", result, "/ 기대:", expected)
print("점수:", score, "/", len(TESTS))
