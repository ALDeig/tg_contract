import json
import os


def insert_data(type_request: str) -> None:
    with open(os.path.join("db", "analytics.json"), 'r', encoding='UTF-8') as f:
        # data = json.loads(f.read())
        data = json.load(f)

    data[type_request] += 1
    with open(os.path.join("db", "analytics.json"), 'w', encoding='UTF-8') as f:
        # f.write(json.dumps(data, ensure_ascii=False))
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_analytics():
    with open(os.path.join("db", "analytics.json"), 'r') as f:
        # data = json.loads(f.read())
        data = json.load(f)

    return data
