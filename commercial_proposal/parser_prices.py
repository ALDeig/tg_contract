import json
import os
import random
from time import sleep

import lxml.html
import requests

# from lxml import etree

tinko_urls1 = ('https://www.tinko.ru/catalog/product/288314/', 'https://www.tinko.ru/catalog/product/016002/',
               'https://www.tinko.ru/catalog/product/261948/', 'https://www.tinko.ru/catalog/product/261949/',
               'https://www.tinko.ru/catalog/product/261950/', 'https://www.tinko.ru/catalog/product/261951/',
               'https://www.tinko.ru/catalog/product/261952/')

hi_watch_urls1 = ('https://hi.watch/product/ds_i253', 'https://hi.watch/product/ds_i250',
                  'https://hi.watch/product/ds_i214wb', 'https://hi.watch/product/ds_n304b',
                  'https://hi.watch/product/ds_n308b', 'https://hi.watch/product/ds_n308_2b',
                  'https://hi.watch/product/ds_n316b', 'https://hi.watch/product/ds_n316_2_b',
                  'https://hi.watch/product/ds_s504pb', 'https://hi.watch/product/ds_s908pb',
                  'https://hi.watch/product/ds_s1816pb', 'https://hi.watch/product/ds_s2624pb',
                  'https://hi.watch/product/ds_1280zj_s', 'https://hi.watch/product/ds_1280zj_xs',
                  'https://hi.watch/product/ds_1ln5e_e_e')

prices_tinko = ('junction_box', 'corrugated_pipe', '1tb', '2tb', '3tb', '4tb', '6tb')

prices_hi_watch = ('dome_cam', 'cylindrical_cam', 'compact_cam', 'rec4cam1d', 'rec8cam1d', 'rec8cam2d', 'rec16cam1d',
                   'rec16cam2d', 'switch4', 'switch8', 'switch16', 'switch24', 'bracket_dome', 'bracket_cyl',
                   'cctv_cable')


def _get_html(url):
    html_text = requests.get(url)

    return html_text


def get_name(url):
    html = _get_html(url)
    tree = lxml.html.document_fromstring(html.text)
    name = tree.xpath('//*[@class="uk-width-large-2-3 uk-width-medium-2-3 uk-width-small-1-1 uk-margin-bottom"]/h3/strong/text()')

    return name[0]


def _parser_hi_watch(url):
    html_text = _get_html(url)
    tree = lxml.html.document_fromstring(html_text.text)
    text_price = tree.xpath('//*[@class="hik-price"]/text()')
    text_name = tree.xpath('//*[@class="uk-width-large-2-3 uk-width-medium-2-3 uk-width-small-1-1 uk-margin-bottom"]/'
                           'h3/strong/text()')
    text_model = tree.xpath('//*[@class="uk-width-1-1 uk-margin-bottom"]/h1/text()')
    price = text_price[0].replace('\xa0', '')[:-2]
    name = text_name[0]
    # price = str()
    # for i in text_price[0]:
    #     if i.isdigit():
    #         price += i

    return {'price': price, 'name': name, 'model': text_model[0].strip()}
# print(_parser_hi_watch('https://hi.watch/product/ds_1280zj_s'))

def _parser_tinko(url):
    html_text = _get_html(url)
    tree = lxml.html.document_fromstring(html_text.text)
    text_price = tree.xpath('//*[@class="product-detail__price-value"]/text()')[0]
    text_name = tree.xpath('//*[@class="page-title product-detail__title "]/h1/text()')
    text_model = tree.xpath('//*[@class="product-detail__property"][3]/span[2]/text()')
    model = text_model[0].strip('\n').strip('\t')
    # print(text_name)
    # return
    text_price = text_price.replace(',', '.').replace(' ', '')
    name = text_name[0]

    return {'price': text_price, 'name': name, 'model': model}

# print(_parser_tinko('https://www.tinko.ru/catalog/product/261948/'))

# _parser_tinko('https://www.tinko.ru/catalog/product/261948/')
def _get_prices_from_hiwatch(prices: dict):
    cnt = 0
    for url in hi_watch_urls1:
        price = _parser_hi_watch(url)
        prices[prices_hi_watch[cnt]] = price
        cnt += 1
        # print(cnt)
        sleep(random.uniform(0.2, 0.8))

    return prices


def _get_prices_from_tinko(prices: dict):
    cnt = 0
    for url in tinko_urls1:
        price = _parser_tinko(url)
        prices[prices_tinko[cnt]] = price
        cnt += 1
        # print(cnt)
        sleep(random.uniform(0.2, 0.8))

    return prices


def _get_prices():
    tmp_prices = _get_prices_from_hiwatch(prices=dict())
    prices = _get_prices_from_tinko(tmp_prices)

    return prices


def save_prices():
    prices = _get_prices()
    # prices = {'a': 1, 'b': 2}
    with open('prices.json', 'w', encoding='UTF-8') as file:  # os.path.join("commercial_proposal", "prices.json")
        file.write(json.dumps(prices, ensure_ascii=False))


def open_prices():
    with open('prices.json', 'r', encoding='UTF-8') as file:
        prices = json.loads(file.read())

    return prices


# save_prices()
