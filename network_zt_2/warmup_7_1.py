import ipaddress              # import 로 파이썬에 들어 있는 IP 계산 모듈 ipaddress 를 불러온다

my_ip = "172.16.8.40"         # 변수 my_ip 에 새 회사 PC 의 IPv4 주소 글자를 담는다
prefix = 24                   # 변수 prefix 에 CIDR 숫자 24 를 담는다

# f-string 으로 「주소/CIDR」 글자를 만들고, strict=False 로 그 주소가 속한 망 객체를 만들어 net 에 담는다
net = ipaddress.ip_network(f"{my_ip}/{prefix}", strict=False)

print(net.netmask)            # .netmask 는 망 객체의 서브넷 마스크다. 그 값을 출력한다
print(net.network_address)    # .network_address 는 망에서 가장 작은 주소다. 그 값을 출력한다
print(net.broadcast_address)  # .broadcast_address 는 망에서 가장 큰 주소다. 그 값을 출력한다
