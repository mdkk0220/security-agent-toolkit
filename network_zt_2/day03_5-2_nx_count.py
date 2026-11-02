logs = [("10.20.0.15", "www.naver.com", "NOERROR"),    # DNS 로그를 (PC 주소, 물어본 이름, 응답) 튜플의 리스트로 만든다
        ("10.20.0.42", "kxq3vz9a.top", "NXDOMAIN"),    # 10.20.0.42 가 없는 이름을 물은 줄이다
        ("10.20.0.42", "p0w8rk2mzq.xyz", "NXDOMAIN"),  # 같은 PC 가 또 없는 이름을 물은 줄이다
        ("10.20.0.33", "nevar.com", "NXDOMAIN"),  # 다른 PC 가 철자를 틀린 이름을 물은 줄이다
        ("10.20.0.42", "zzx9q2lk.top", "NXDOMAIN"),    # 10.20.0.42 가 세 번째로 없는 이름을 물은 줄이다
        ("10.20.0.42", "qwrtpzkx7v.com", "NOERROR")]   # 10.20.0.42 가 마지막에 응답을 받은 줄이다
nx = {}                                                # PC 주소별 NXDOMAIN 횟수를 담을 빈 딕셔너리를 만든다
for pc, name, rcode in logs:                           # 튜플을 하나씩 꺼내 세 값을 pc · name · rcode 에 나눠 담아 반복한다
    if rcode == "NXDOMAIN":                            # 응답이 NXDOMAIN 이면 아래 줄을 실행한다
        nx[pc] = nx.get(pc, 0) + 1                     # 그 PC 의 횟수를 1 늘린다
print(nx)                                              # PC 주소별 NXDOMAIN 횟수를 출력한다
