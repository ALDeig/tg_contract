import json


def insert_data(type_request: str) -> None:
    with open('analytics.json', 'r', encoding='UTF-8') as f:
        data = json.loads(f.read())

    data[type_request] += 1
    with open('analytics.json', 'w', encoding='UTF-8') as f:
        f.write(json.dumps(data, ensure_ascii=False))


def get_analytics():
    with open('analytics.json', 'r') as f:
        data = json.loads(f.read())

    return data
