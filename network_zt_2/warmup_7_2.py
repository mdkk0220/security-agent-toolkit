import ipaddress                                    # import 로 파이썬에 들어 있는 IP 계산 모듈 ipaddress 를 불러온다

parent = ipaddress.ip_network("192.168.50.0/24")    # 나눌 전체 망 192.168.50.0/24 를 망 객체로 만들어 parent 에 담는다

for block in parent.subnets(new_prefix=27):         # .subnets(new_prefix=27) 이 /27 블록을 하나씩 리턴하고, 그 블록을 block 에 담아 반복한다
    print(block)                                    # 블록을 「네트워크 주소/CIDR」 꼴로 출력한다
