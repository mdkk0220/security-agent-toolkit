import socket                                 # import 로 네트워크 도구 모음 socket 을 불러온다
url = "https://example.com/news/today"        # 주소창에 친 URL 글자를 url 에 담는다
parts = url.split("/")                        # split("/") 로 URL 을 / 마다 잘라 리스트를 parts 에 담는다
name = parts[2]                               # 리스트의 번호 2 칸(0 번부터 세어 셋째 칸)을 꺼내 name 에 담는다
print(parts)                                  # 리스트 전체를 출력한다
print(name, "→", socket.gethostbyname(name))  # name 과, gethostbyname() 이 DNS 서버에 물어 리턴한 IPv4 주소를 함께 출력한다
