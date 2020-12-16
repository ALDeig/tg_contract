import json
import os

import db
from commercial_proposal.parserlinks import ParserLinks
from commercial_proposal.parserdata import ParserCameras

# links = ParserLinks()
# links.main()


def get_information_of_cameras():
    with open(os.path.join('commercial_proposal', 'links_hiwatch.json'), 'r', encoding='utf-8') as file:
        links = json.load(file)
    data = ParserCameras(urls=links, brand='hiwatch')
    data = data.run()
    return data


def insert_information():
    data = get_information_of_cameras()
    # для теста:
    cnt = 1
    res = {}
    for i in data:
        res[cnt] = i
        cnt += 1
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(res, file, indent=4, ensure_ascii=False)

    # конец теста
    db.insert_data_of_cameras(data)
