from config_loader import load_json

PATHS = [
    "config/users.json",
    "config/users_typo.json",
    "config/users_broken.json",
]

for path in PATHS:
    users = load_json(path, {})
    if "seoyeon" in users:
        print(path, "-> 사용자", len(users), "명을 읽음, 판정을 계속한다")
    else:
        print(path, "-> 사용자 0 명, 등록된 사용자가 없다")
