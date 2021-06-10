from datetime import date
import locale
import os
import re
import shutil

from docxtpl import DocxTemplate
from num2words import num2words

import db

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


def create_copy_template(name: str, number: str) -> None:
    shutil.copy(os.path.join('contracts', name), number)


def _get_data_client_from_api(inn_answer: dict, bik_answer: dict) -> dict:
    initials_cl = inn_answer['initials'].split()
    initials_cl = f'{initials_cl[0]} {initials_cl[-2][0]}. {initials_cl[-1][0]}.'
    data_client_from_inn = {'name_client': inn_answer['name_ip'],
                            'director_cl': inn_answer['initials'],
                            'ogrn_client': inn_answer['ogrn'],
                            'address_cl': inn_answer['address'],
                            'kpp': inn_answer['kpp'],
                            'initials_cl': initials_cl}

    data_client_from_bik = {'name_bank_cl': bik_answer['name_bank'],
                            'cor_acc_client': bik_answer['number_account']}
    data_client_from_inn.update(data_client_from_bik)

    return data_client_from_inn


def _get_data_client_from_api_ip(inn: dict, bik: dict) -> dict:
    initials_cl = inn['name_ip'].split()
    initials_cl = f'{initials_cl[0]} {initials_cl[-2][0]}. {initials_cl[-1][0]}.'
    data_client_from_inn = {'name_client': inn['name_ip'],
                            'ogrn_client': inn['ogrn'],
                            'address_cl': inn['address'],
                            'initials_cl': initials_cl}

    data_client_from_bik = {'name_bank_cl': bik['name_bank'],
                            'cor_acc_client': bik['number_account']}
    data_client_from_inn.update(data_client_from_bik)

    return data_client_from_inn


def _calculate_the_advance_and_the_last_payment_with_nds(price: str, prepaid: str) -> tuple:
    if prepaid != '100':
        advance = f'{float(price) / 100 * float(prepaid):.2f}'
        nds_advance = f'{(float(advance) / 1.2 * 0.2):.2f}'
        last_payment = f'{float(price) - float(advance):.2f}'
        nds_last_payment = f'{(float(last_payment) / 1.2 * 0.2):.2f}'
        price_tmp = f'{float(price):.2f}'
        nds = f"{(float(price) / 1.2 * 0.2):.2f}"

        advance_str = f"{int(float(advance))} ({num2words(int(float(advance)), lang='ru')}) руб. {advance.split('.')[-1]} "\
                      f"коп., в том числе НДС {nds_advance.split('.')[0]} " \
                      f"({num2words(nds_advance.split('.')[0], lang='ru')}) руб. {nds_advance.split('.')[-1]} коп."
        last_payment_str = f"{last_payment.split('.')[0]} ({num2words(int(float(last_payment)), lang='ru')}) руб. " \
                           f"{last_payment.split('.')[-1]} коп., в том числе НДС " \
                           f"{nds_last_payment.split('.')[0]} ({num2words(nds_last_payment.split('.')[0], lang='ru')}) "\
                           f"руб. {nds_last_payment.split('.')[-1]} коп."
        price_new = f"{price.split('.')[0]} ({num2words(int(price.split('.')[0]), lang='ru')}) руб. " \
                    f"{str(price_tmp).split('.')[-1]} коп, в том числе НДС {nds.split('.')[0]} " \
                    f"({num2words(int(nds.split('.')[0]), lang='ru')}) руб. {nds.split('.')[-1]} коп."
    else:
        price_tmp = f"{float(price):.2f}"
        nds = f"{(float(price) / 1.2 * 0.2):.2f}"
        price_new = f"{price.split('.')[0]} ({num2words(int(price.split('.')[0]), lang='ru')}) руб. " \
                    f"{str(price_tmp).split('.')[-1]} коп, в том числе НДС {nds.split('.')[0]} " \
                    f"({num2words(int(nds.split('.')[0]), lang='ru')}) руб. {nds.split('.')[-1]} коп."
        last_payment_str = None
        advance_str = None

    return advance_str, last_payment_str, price_new


def _calculate_the_advance_and_the_last_payment(price: str, prepaid: str) -> tuple:
    if prepaid != '100':
        advance = float(price) / 100 * float(prepaid)
        advance_kop = f"{advance:.2f}"
        advance_str = f"{int(advance)} ({num2words(int(advance), lang='ru')}) руб. {str(advance_kop).split('.')[-1]} коп."
        last_payment = float(price) - advance
        last_payment_kop = f"{last_payment:.2f}"
        last_payment_str = f"{int(last_payment)} ({num2words(int(last_payment), lang='ru')}) руб. " \
                        f"{str(last_payment_kop).split('.')[-1]} коп."
        price_tmp = f"{float(price):.2f}"
        price_new = f"{price.split('.')[0]} ({num2words(int(price.split('.')[0]), lang='ru')}) руб. " \
                    f"{str(price_tmp).split('.')[-1]} коп."
    else:
        price_tmp = f"{float(price):.2f}"
        price_new = f"{price.split('.')[0]} ({num2words(int(price.split('.')[0]), lang='ru')}) руб. " \
                    f"{str(price_tmp).split('.')[-1]} коп."
        advance_str = None
        last_payment_str = None

    return advance_str, last_payment_str, price_new


def choice_of_ending(number: str) -> str:
    endings = {'1': 'день', '2': 'дня', '3': 'дня', '4': 'дня', '5': 'дней', '6': 'дней', '7': 'дней', '8': 'дней',
               '9': 'дней', '0': 'дней'}
    endings_2 = {'11': 'дней', '12': 'дней', '13': 'дней'}
    try:
        ending = endings_2[number[-2:]]
    except KeyError:
        ending = endings[number[-1]]

    endings_3 = {'день': 'календарный', 'дней': 'календарных', 'дня': 'календарных'}
    result = endings_3[ending] + ' ' + ending

    return result


def transform_period(period: str):
    ending = choice_of_ending(period)
    result = f"{period} ({num2words(int(period), lang='ru')}) {ending}"

    return result


def get_file_name(name, type_executor, nds) -> str:
    """Получает имя шаблона исходя из данных договора"""
    if type_executor == 'ЮЛ':
        name += 'ooo'
    else:
        name += 'ip'

    if nds[0] != 'у':
        name += 'n'

    name += '.docx'
    return name


def create_new_file_name(name_contract: str) -> str:
    """Создает имя для файла нового договора из номера договора убирая из него лишние символы"""
    name = ''
    for word in name_contract:
        if word in re.findall(r"[a-zа-я0-9_]", word, re.IGNORECASE):
            name += word

    return name + '.docx'


def get_data_from_db_and_api(id_tg: int, data: dict) -> tuple:
    cursor = db.get_cursor()
    cursor.execute(f"SELECT type_executor FROM users WHERE id_tg={id_tg}")
    type_executor = cursor.fetchone()[0]
    if type_executor == 'ЮЛ':
        context = db.get_data_from_db_ooo(id_tg=id_tg)
    else:
        context = db.get_data_from_db_ip(id_tg=id_tg)
    if data['api_inn'][1] == 'ИП':
        data_client_from_api = _get_data_client_from_api_ip(inn=data['api_inn'][0], bik=data['api_bik'])
    else:
        data_client_from_api = _get_data_client_from_api(data['api_inn'][0], data['api_bik'])

    context.update(data_client_from_api)
    name = get_file_name(data['name_file'], type_executor, context['taxation'])

    return context, name


def filling_contract(data: dict, id_tg: int) -> str:
    today = date.today()
    all_data = get_data_from_db_and_api(id_tg=id_tg, data=data)
    context = all_data[0]
    if context['taxation'][0] == 'у':
        payments = _calculate_the_advance_and_the_last_payment(data['price'], data['prepaid'])
    else:
        payments = _calculate_the_advance_and_the_last_payment_with_nds(data['price'], data['prepaid'])
    name_pattern = all_data[1]
    name_contract = create_new_file_name(context['number'])
    initials_ex = context['director_ex'].split()
    initials_ex = f'{initials_ex[0]} {initials_ex[-2][0]}. {initials_ex[-1][0]}.'
    create_copy_template(name_pattern, name_contract)
    doc = DocxTemplate(name_contract)
    period = transform_period(data['period'])
    context.update({'address_work': data['address'],
                    'last_payment': payments[1],
                    'price': payments[2],
                    'prepaid': payments[0],
                    'period': period,
                    'day': today.strftime('%d'),
                    'month': today.strftime('%B'),
                    'year': today.strftime('%Y'),
                    'bik_client': data['bik'],
                    'inn_client': data['inn'],
                    'check_acc_client': data['current_account'],
                    'initials_ex': initials_ex
                    })
    doc.render(context)
    doc.save(name_contract)

    return name_contract
