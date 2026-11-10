def lookup_account(entity, users_info):
    account = {"employed": False, "vip": False}
    if entity in users_info:
        account["employed"] = users_info[entity]["employed"]
        account["vip"] = users_info[entity]["vip"]
    return account


def lookup_source_ip(entity, source_ips, trusted_ips):
    ip_info = {"source_ip": None, "ip_trusted": False}
    if entity in source_ips:
        ip_info["source_ip"] = source_ips[entity]
        ip_info["ip_trusted"] = source_ips[entity] in trusted_ips
    return ip_info


def enrich_incident(incident, users_info, source_ips, trusted_ips):
    entity = incident["entity"]
    account = lookup_account(entity, users_info)
    ip_info = lookup_source_ip(entity, source_ips, trusted_ips)
    incident["context"] = {
        "account_known": entity in users_info,
        "employed": account["employed"],
        "vip": account["vip"],
        "source_ip": ip_info["source_ip"],
        "ip_trusted": ip_info["ip_trusted"],
    }
    return incident
