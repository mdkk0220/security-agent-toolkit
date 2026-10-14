LOG = [("news.dailybrief.com", "NOERROR", "정상"), ("cafe-mocha-roasters.xyz", "NOERROR", "정상"),   # 예시 6건이다. (이름, 응답, 실제) 튜플의 리스트로 만들고, 이 건들을 내가 만든 6건으로 바꾼다
       ("intranet-old-wiki.top", "NXDOMAIN", "정상"), ("k3x9qz7wm2.com", "NXDOMAIN", "의심"),         # 정상 이름이 NXDOMAIN 이 되는 경우와 DGA 모양 이름의 예다
       ("secure-pay-bank.net", "NOERROR", "의심"), ("zxqv1.tk", "NXDOMAIN", "의심")]                  # 사칭 이름과 짧은 DGA 이름의 예다
for name, rcode, truth in LOG:                    # 튜플을 하나씩 꺼내 이름은 name, 응답은 rcode, 실제는 truth 에 나눠 담아 반복한다
    parts = name.split(".")                       # 이름을 점으로 나눈 리스트를 parts 에 담는다
    score = 0                                     # 이 이름의 점수를 0 으로 시작한다
    if len(parts[-2]) >= 10:                      # 규칙 ①: TLD 바로 앞 레이블이 10글자 이상이면
        score = score + 1                         # 1점을 더한다
    if parts[-1] in ["top", "xyz", "tk"]:         # 규칙 ②: TLD 가 세 값 가운데 하나이면
        score = score + 1                         # 1점을 더한다
    if rcode == "NXDOMAIN":                       # 규칙 ③: 응답이 NXDOMAIN 이면
        score = score + 2                         # 2점을 더한다
    print(name, score, score >= 3, "실제:", truth)  # 이름 · 점수 · 규칙의 판정(True 가 의심) · 실제를 한 줄에 출력한다
