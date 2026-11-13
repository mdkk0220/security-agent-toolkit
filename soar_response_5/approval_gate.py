def is_allowlisted(request, policy):
    return request["target"] in policy["allowlist_ips"]


def risk_score(request, policy):
    grade_table = policy["grade_points"]
    score = grade_table[request["grade"]]
    reasons = ["등급 " + request["grade"] + " +" + str(score)]
    if request["target"] in policy["vip_accounts"]:
        score = score + policy["vip_points"]
        reasons.append("VIP 계정 +" + str(policy["vip_points"]))
    if request["users_on_ip"] >= policy["shared_ip_limit"]:
        score = score + policy["shared_ip_points"]
        reasons.append("함께 쓰는 IP +" + str(policy["shared_ip_points"]))
    if request["target_count"] > policy["many_targets_limit"]:
        score = score + policy["many_targets_points"]
        reasons.append("대상 " + str(request["target_count"]) + "개 +" + str(policy["many_targets_points"]))
    return score, reasons


def decide_gate(request, policy):
    if is_allowlisted(request, policy):
        return "차단 금지", ["허용 목록 대상"]
    score, reasons = risk_score(request, policy)
    reasons.append("합계 " + str(score) + "점")
    if score >= policy["approval_score"]:
        return "승인 필요", reasons
    return "자동", reasons
