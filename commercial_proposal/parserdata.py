import os
from random import randint
import time

from bs4 import BeautifulSoup
import requests
import urllib.request


class ParserCameras:

    def __init__(self, urls: dict, brand: str):
        self.urls = urls
        self.brand = brand
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            'Accept-Language': 'ru'
        }

    def get_url(self):
        links = []
        for key, value in self.urls.items():
            key = key.split('_')
            key.append(value)
            links.append(key)

        return links

    def load_page(self, url):
        res = self.session.get(url=url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'lxml')

        return soup

    @classmethod
    def load_image(cls, url, name):
        img = urllib.request.urlopen(url).read()
        with open(os.path.join('commercial_proposal', 'images', name + '.jpg'), 'wb') as file:
            file.write(img)

    @classmethod
    def parse_page(cls, soup: BeautifulSoup):
        model = soup.find(class_='uk-width-1-1 uk-margin-bottom').find('h1').text.strip()
        block_descriptions = soup.find('div', class_='uk-width-large-2-3 uk-width-medium-2-3 uk-width-small-1-1 uk-margin-bottom')
        description = block_descriptions.find('h3').text.strip()
        specifications = block_descriptions.find('p').text.strip()
        price = block_descriptions.find('span').text.replace('\xa0', '')[:-2]
        block_image = soup.find('div', class_='uk-width-large-1-3 uk-width-medium-1-3 uk-width-small-1-1 uk-margin-bottom')
        link_image = 'https://hi.watch' + block_image.find('a').get('href')
        cls.load_image(link_image, model)

        return [model, description, specifications, price, model + '.jpg']

    def run(self):
        links = self.get_url()
        data = []
        for item in links:
            if len(item[3]) > 0:
                for url in item[3]:
                    soup = self.load_page(url)
                    result = self.parse_page(soup)
                    result.extend(item[:-1])
                    result.append(self.brand)
                    data.append(result)
                    time.sleep(randint(1, 3))

        return data
        # soup = self.load_page('https://hi.watch/product/ds_t203l')
        # result = self.parse_page(soup)