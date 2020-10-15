import os
from time import time

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Pt
# from docx.styles import style

# document = Document('test1.docx')
# parars = document.tables
# table = parars[0]
# print(table.style.name)
# document = Document('Doc1.docx')
# data = (('1dsfasdfsdf', '2', '3', '4', '5'),
#         ('6asdfsdafsdf sdfasdfs safasfsfsfasf asfasfs', '7', '8', '9', '10'),
#         ('Итог', ),
#         ('11 asfasfs f safasdfasfsad s as', '12', '13', '14', '15'))
# table = document.add_table(rows=1, cols=5, style='Table Grid')
# table.alignment = WD_TABLE_ALIGNMENT.RIGHT
# # sys.exit()
# hdr_cells = table.rows[0].cells
# hdr_cells[0].text = '1 column dsafds asdfadsfds fsdf asfa sfds af sf safd safkk'
# hdr_cells[0].height = 5
# hdr_cells[1].text = '2 column'
# hdr_cells[2].text = '3 column'
# hdr_cells[3].text = '4 column'
# hdr_cells[4].text = '5 column'
# document.save('test_003.docx')


def gen_name_file():
    file_name = f'file-{int(time()) * 100}.docx'

    return file_name


def save_kp(table_data, total_price):
    document = Document(os.path.join('commercial_proposal', 'Doc1.docx'))
    # document = Document('Doc1.docx')
    table = document.add_table(rows=3, cols=1, style='Table Grid')
    table.add_column(625)
    table.add_column(1500000)
    table.add_column(1500000)
    table.add_column(1500000)
    hdr_1_cells = table.rows[0].cells
    cell = hdr_1_cells[1].merge(hdr_1_cells[3])
    cell.text = 'Общая стоимость'
    run = cell.paragraphs[0].runs[0]
    run.font.bold = True
    run.font.size = Pt(16)
    hdr_1_cells[4].text = f'{total_price:.2f}'
    run = hdr_1_cells[4].paragraphs[0].runs[0]
    run.font.size = Pt(16)
    row_2 = table.rows[1].cells
    row_2[0].merge(row_2[4])
    hdr_cells = table.rows[2].cells
    hdr_cells[0].text = 'Наименование'
    hdr_cells[1].text = 'Ед. из.'
    hdr_cells[2].text = 'Кол-во'
    hdr_cells[3].text = 'Цена, руб.'
    hdr_cells[4].text = 'Сумма, руб.'
    for rows in table_data:
        cnt = 0
        row = table.add_row()
        row.height = 2
        row_cells = row.cells
        if len(rows) == 1:
            cell = row_cells[cnt].merge(row_cells[4])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cell.text = rows[0]
            cell.paragraphs[0].paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            run = cell.paragraphs[0].runs[0]
            run.font.bold = True
            run.font.size = Pt(14)
            continue
        for data in rows:
            row_cells[cnt].text = str(data)
            cnt += 1
    file_name = gen_name_file()
    document.save(file_name)

    return file_name


# save_kp(data, 19999)

