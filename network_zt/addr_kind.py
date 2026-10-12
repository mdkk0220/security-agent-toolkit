def kind(address):                                # 주소의 모양을 보고 종류를 리턴하는 함수
    # 1. address 를 "." 로 나눈 조각이 4개이면 "IP" 를 return 하세요
    if address.count(".") == 3:
        return "IP"
    # 2. address 를 "-" 로 나눈 조각이 6개이면 "MAC" 을 return 하세요
    if address.count("-") == 5:
        return "MAC"
    # 3. 둘 다 아니면 "모름" 을 return 하세요
    return "모름"

# ── 미리 채워 둔 줄입니다. 고치지 않습니다 ──
for a in ["192.168.0.15", "a8-5e-45-01-2b-3c", "ff-ff-ff-ff-ff-ff", "192.168.0"]:
    print(kind(a), a)                             # 종류와 주소를 한 줄에
# ── 여기까지 ──
