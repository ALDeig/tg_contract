import os

from docx.opc.exceptions import PackageNotFoundError
from docxtpl import DocxTemplate, RichText
from db import get_number_kp, get_kp_tpl


def gen_name_file(id_tg):
    number_kp = get_number_kp(id_tg)
    file_name = f'КП-{number_kp}.docx'

    return file_name, number_kp


def save_kp(table_data, total_price, id_tg):
    tpl_name = get_kp_tpl(id_tg)
    if tpl_name is None:
        tpl_name = os.path.join('documents', 'default.docx')

    tpl = DocxTemplate(tpl_name)
    context = {
        'price': total_price,
        'tbl_contents': []
    }

    for item in table_data:
        if len(item) == 1:
            context['tbl_contents'].append({'label': RichText(text=item[0], size=30, bold=True, color='000000')})
        else:
            context['tbl_contents'].append({'label': item[0], 'c1': item[1], 'c2': item[2], 'c3': item[3], 'c4': item[4]})
    file_name, number_kp = gen_name_file(id_tg)
    tpl.render(context)
    tpl.save(file_name)

    return file_name, number_kp


def save_table_to_provider(data, id_tg):
    tpl_name = os.path.join('documents', 'to_provider.docx')
    tpl = DocxTemplate(tpl_name)
    context = {
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

# def save_kp1(table_data, total_price, id_tg):
#     document = Document(os.path.join('commercial_proposal', 'Doc1.docx'))
#     # document = Document('Doc1.docx')
#     table = document.add_table(rows=3, cols=1, style='Table Grid')
#     table.add_column(625)
#     table.add_column(1500000)
#     table.add_column(1500000)
#     table.add_column(1500000)
#     hdr_1_cells = table.rows[0].cells
#     cell = hdr_1_cells[1].merge(hdr_1_cells[3])
#     cell.text = 'Общая стоимость'
#     run = cell.paragraphs[0].runs[0]
#     run.font.bold = True
#     run.font.size = Pt(16)
#     hdr_1_cells[4].text = f'{total_price:.2f}'
#     run = hdr_1_cells[4].paragraphs[0].runs[0]
#     run.font.size = Pt(16)
#     row_2 = table.rows[1].cells
#     row_2[0].merge(row_2[4])
#     hdr_cells = table.rows[2].cells
#     hdr_cells[0].text = 'Наименование'
#     hdr_cells[1].text = 'Ед. из.'
#     hdr_cells[2].text = 'Кол-во'
#     hdr_cells[3].text = 'Цена, руб.'
#     hdr_cells[4].text = 'Сумма, руб.'
#     for rows in table_data:
#         cnt = 0
#         row = table.add_row()
#         row.height = 2
#         row_cells = row.cells
#         if len(rows) == 1:
#             cell = row_cells[cnt].merge(row_cells[4])
#             cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
#             cell.text = rows[0]
#             cell.paragraphs[0].paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
#             run = cell.paragraphs[0].runs[0]
#             run.font.bold = True
#             run.font.size = Pt(14)
#             continue
#         for data in rows:
#             row_cells[cnt].text = str(data)
#             cnt += 1
#     file_name, number_kp = gen_name_file(id_tg)
#     document.save(file_name)
#
#     return file_name, number_kp
