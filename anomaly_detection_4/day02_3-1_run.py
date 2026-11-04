from normalize_json_csv import load_server, load_saas

server_events = load_server("server_log.jsonl")
saas_events = load_saas("saas_events.csv")

server_count = len(server_events)
server_counts = {}
for event in server_events:
    result = event["result"]
    server_counts[result] = server_counts.get(result, 0) + 1
print("--- 단계 1: 판정 서버 이벤트", server_count, "개")
print(server_counts)

saas_count = len(saas_events)
saas_counts = {}
for event in saas_events:
    result = event["result"]
    saas_counts[result] = saas_counts.get(result, 0) + 1
print("--- 단계 2: SaaS 이벤트", saas_count, "개")
print(saas_counts)

first_server = server_events[0]
first_saas = saas_events[0]
print("--- 단계 3: 각 로그의 첫 이벤트")
print(first_server)
print(first_saas)
