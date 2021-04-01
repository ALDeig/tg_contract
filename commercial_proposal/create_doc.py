import os
from datetime import date

from docx.opc.exceptions import PackageNotFoundError
from docxtpl import DocxTemplate, RichText

import db
from db import get_number_kp, get_kp_tpl


def gen_name_file(id_tg):
    number_kp = get_number_kp(id_tg)
    file_name = f'КП-{number_kp}.docx'

    return file_name, number_kp


def save_kp(table_data, total_price, id_tg):
    tpl_name = get_kp_tpl(id_tg)
    if tpl_name is None:
        tpl_name = os.path.join('documents', 'template_kp.docx')

    user_data = db.get_data('name, phone, city', 'users', {'id_tg': ('=', id_tg)})[0]
    organization_data = ('ip', db.get_data('name_ip, inn', 'executor_ip', {'user_id_tg': ('=', id_tg)}))
    if not organization_data[1]:
        organization_data = ('ooo', db.get_data('name_org, inn', 'executor_ooo', {'user_id_tg': ('=', id_tg)}))
    tpl = DocxTemplate(tpl_name)
    today = date.today().strftime('%d-%m-%Y')
    context = {
        'date': today,
        'name': user_data.name,
        'phone': user_data.phone,
        'city': user_data.city,
        'price': total_price,
        'tbl_contents': []
    }
    if organization_data[1]:
        prefix = 'ИП' if organization_data[0] == 'ip' else 'ООО'
        context.update({'inn': organization_data[1][0].inn, 'organization': f'{prefix} {organization_data[1][0][0]}'})

    for item in table_data:
        if len(item) == 1:
            context['tbl_contents'].append({'label': RichText(text=item[0], size=30, bold=True, color='000000')})
        else:
            context['tbl_contents'].append({'label': item[0], 'c1': item[1], 'c2': item[2], 'c3': item[3], 'c4': item[4]})
    file_name, number_kp = gen_name_file(id_tg)
    tpl.render(context)
    tpl.save(file_name)

    return file_name, number_kp


def save_table_to_provider(data, number_order, id_tg):
    tpl_name = os.path.join('documents', 'to_provider_1.docx')
    tpl = DocxTemplate(tpl_name)
    context = {
        'number_order': f'Заказ №{number_order}',
        'tbl_contents': []
    }
    for item in data:
        if len(item) == 1:
            context['tbl_contents'].append({'label': RichText(text=item[0], size=30, bold=True, color='000000')})
        else:
            context['tbl_contents'].append({'label': item[0], 'c1': item[1], 'c2': item[2]})
    file_name = f'{id_tg}.docx'
    tpl.render(context)
    tpl.save(file_name)
    return file_name
