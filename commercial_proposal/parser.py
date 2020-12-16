import json
import os

import db
from commercial_proposal.parserlinks import ParserLinks
from commercial_proposal.parserdata import ParserCameras


def parse_links():
    links = ParserLinks()
    links.main()


def get_information_of_cameras():
    with open(os.path.join('commercial_proposal', 'links_hiwatch.json'), 'r', encoding='utf-8') as file:
        links = json.load(file)
    data = ParserCameras(urls=links, brand='hiwatch')
    data = data.run()
    return data


def insert_information():
    parse_links()
    data = get_information_of_cameras()
    db.insert_data_of_cameras(data)
