from datetime import date
import locale
import shutil

from docxtpl import DocxTemplate
from num2words import num2words

import db

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


def create_copy_template(number: str) -> None:
    shutil.copy('contract.docx', f'Договор.docx')


def _get_data_client_from_api(inn_answer, bik_answer) -> dict:
    initials_cl = inn_answer['initials'].split()
    initials_cl = f'{initials_cl[0]} {initials_cl[-2][0]}. {initials_cl[-1][0]}.'
    data_client_from_inn = {'name_client': inn_answer['name_org'],
                            'director_cl': inn_answer['initials'],
                            'ogrn_client': inn_answer['ogrn'],
                            'address_cl': inn_answer['address'],
                            'kpp': inn_answer['kpp'],
                            'initials_cl': initials_cl}

    data_client_from_bik = {'name_bank_cl': bik_answer['name_bank'],
                            'cor_acc_client': bik_answer['number_account']}
    data_client_from_inn.update(data_client_from_bik)

    return data_client_from_inn


def _calculate_the_advance_and_the_last_payment(price: str, prepaid: str) -> tuple:
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

    return advance_str, last_payment_str, price_new


def transform_warranty(warranty: str):
    tmp = ''
    cnt = 0
    for number in warranty:
        if number.isdigit():
            cnt += 1
            tmp = f'{number}{tmp}'
        else:
            break

    number_period = f"{tmp} ({num2words(int(tmp))})"
    period = f'{number_period} {warranty[cnt:]}'

    return period


def filling_contract(data: dict, id_tg: int) -> None:
    today = date.today()
    payments = _calculate_the_advance_and_the_last_payment(data['price'], data['prepaid'])
    cursor = db.get_cursor()
    cursor.execute(f"SELECT type_executor FROM users WHERE id_tg={id_tg}")
    type_executor = cursor.fetchone()[0]
    if type_executor == 'ЮЛ':
        context = db.get_data_from_db_ooo(id_tg=id_tg)
    else:
        context = db.get_data_from_db_ip(id_tg=id_tg)
    initials_ex = context['director_ex'].split()
    initials_ex = f'{initials_ex[0]} {initials_ex[-2][0]}. {initials_ex[-1][0]}.'
    create_copy_template(context['number'])
    doc = DocxTemplate(f"Договор.docx")
    data_client_from_api = _get_data_client_from_api(data['api_inn_'][0], data['api_bik_'])
    context.update(data_client_from_api)
    context.update({'address_work': data['address'],
                    'last_payment': payments[1],
                    'price': payments[2],
                    'prepaid': payments[0],
                    'period': f"{data['period']} ({num2words(int(data['period']), lang='ru')})",
                    'day': today.strftime('%d'),
                    'month': today.strftime('%B'),
                    'bik_client': data['bik'],
                    'inn_client': data['inn'],
                    'check_acc_client': data['current_account'],
                    'initials_ex': initials_ex
                    })
    doc.render(context)
    doc.save(f'Договор.docx')
