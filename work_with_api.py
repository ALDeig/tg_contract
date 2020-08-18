import json
from typing import NamedTuple

import requests

import config


class DataFromApiInn(NamedTuple):
    name_org: str
    initials: str
    position: str
    ogrn: str
    address: str


class DataFromApiBik(NamedTuple):
    name: str
    number_account: str


def _get_data_from_api_inn(inn_egr: str):
    """Получает данные из API по ИНН"""
    result = requests.get(f'https://api-fns.ru/api/egr?req={inn_egr}&key={config.KEY_EGR}')

    return result


def _get_data_from_api_bik(bik):
    """Получает данные из API по БИК Банка"""
    result = requests.get(f'https://analizbankov.ru/api/bankbic?bic={bik}&key={config.KEY_BANK_INFO}')

    return result


def parse_answer_inn(inn_erg: str):
    """Компанует в словарь ответ от API от ИНН"""
    try:
        answer = _get_data_from_api_inn(inn_erg).json()
    except json.JSONDecodeError:
        return False
    if len(answer) == 0:
        return False

    flg = 'ЮЛ'
    try:
        data = answer['items'][0]['ЮЛ']
    except IndexError:
        return False
    except KeyError:
        data = answer['items'][0]['ИП']
        flg = 'ИП'

    if flg == 'ЮЛ':
        result = {'name_org': data['НаимПолнЮЛ'],
                  'initials': data['Руководитель']['ФИОПолн'],
                  'position': data['Руководитель']['Должн'],
                  'ogrn': data['ОГРН'],
                  'kpp': data['КПП'],
                  'address': data['Адрес']['АдресПолн']}
    else:
        result = {'name_ip': data['ФИОПолн'],
                  'ogrn': data['ОГРНИП'],
                  'type_ip': data['ВидИП'],
                  'code_region': data['Адрес']['КодРегион'],
                  'address': data['Адрес']['АдресПолн']}

    return result, flg


def parse_answer_bik(bik):
    """Компанует в словарь ответ от API по БИК"""
    try:
        answer = _get_data_from_api_bik(bik).json()
    except json.JSONDecodeError:
        return False
    if answer['БИК'] is None:
        return False

    result = {'name_bank': answer['Наименование'],
              'number_account': answer['СчетНомер']}

    return result
