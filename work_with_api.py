import json

import requests

import config


def _get_data_from_api_inn(inn_egr: str):
    """Получает данные из API по ИНН"""
    result = requests.get(f'https://api-fns.ru/api/egr?req={inn_egr}&key={config.KEY_EGR}')

    return result


def _get_data_from_api_bik(bik):
    """Получает данные из API по БИК Банка"""
    result = requests.get(f'https://analizbankov.ru/api/bankbic?bic={bik}&key={config.KEY_BANK_INFO}')

    return result


def get_limit_api_inn() -> tuple or bool:
    """Функция возвращает количество запросов, сколько заросов использовано и сколько осталось.
    По методу ИНН"""
    result = requests.get(f'https://api-fns.ru/api/stat?key={config.KEY_EGR}')
    try:
        data_json = result.json()
    except json.JSONDecodeError:
        return False
    try:
        limit = data_json['Методы']['egr']['Лимит']
        spend = data_json['Методы']['egr']['Истрачено']
        expiration_date = data_json['ДатаОконч']
    except KeyError:
        return False
    left = int(limit) - int(spend)

    return limit, spend, left, expiration_date


def get_limit_api_bik() -> tuple or bool:
    """Функция возвращает количество запросов, сколько заросов использовано и сколько осталось.
    По методу bic"""
    result = requests.get(f'https://analizbankov.ru/api/stat?key={config.KEY_BANK_INFO}')
    try:
        data_json = result.json()
    except json.JSONDecodeError:
        return False
    try:
        limit = data_json['Методы']['bankbic']['Лимит']
        spend = data_json['Методы']['bankbic']['Истрачено']
        expiration_date = data_json['ДатаОконч']
    except KeyError:
        return False
    left = int(limit) - int(spend)

    return limit, spend, left, expiration_date


def parse_answer_inn(inn_erg: str):
    """Компанует в словарь ответ от API по ИНН"""
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
        data_address = data['История']['Адрес']
        for i in data_address.keys():
            try:
                address = data_address[i]['АдресПолн']
            except KeyError:
                address = data['Адрес']['АдресПолн']
            break

    if flg == 'ЮЛ':
        result = {'name_ip': data['НаимПолнЮЛ'],
                  'initials': data['Руководитель']['ФИОПолн'],
                  'position': data['Руководитель']['Должн'],  # не нужна
                  'ogrn': data['ОГРН'],
                  'kpp': data['КПП'],
                  'address': data['Адрес']['АдресПолн']}
    else:
        result = {'name_ip': data['ФИОПолн'],
                  'ogrn': data['ОГРНИП'],
                  'type_ip': data['ВидИП'],
                  'code_region': data['Адрес']['КодРегион'],
                  'address': address}  # data['Адрес']['АдресПолн']}

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
