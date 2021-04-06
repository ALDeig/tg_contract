from decimal import Decimal

import db
from commercial_proposal import parser_prices
from commercial_proposal.analog_kp.recorder_and_hdd import Recorders, RowRecorderAndHDD
# from commercial_proposal.analog_kp.row_switch import Switch, RowsSwitch
from commercial_proposal.analog_kp.row_locker import Locker
from commercial_proposal.analog_kp import row_other


def calculate_fasteners(type_cam_in_room, type_cam_on_street, cams_in_room, cams_on_street):
    """Вычисляет крепежные элементы для камер"""
    result = {'junction_box': 0, 'bracket_cyl': 0, 'bracket_dome': 0}
    if type_cam_in_room == 'Компактная':
        result['junction_box'] += cams_in_room
    elif type_cam_in_room == 'Цилиндрическая':
        result['bracket_cyl'] += cams_in_room
    elif type_cam_in_room == 'Купольная':
        result['bracket_dome'] += cams_in_room
    if type_cam_on_street == 'Цилиндрическая':
        result['bracket_cyl'] += cams_on_street
    elif type_cam_on_street == 'Купольная':
        result['bracket_dome'] += cams_on_street

    return result


def calculate_meter(total_cam, mt_cam):
    """Вычисляет количество метров кабеля"""
    cctv_cable = total_cam * mt_cam

    return cctv_cable


def count_equipment(data: list) -> dict:
    """Из списка оборудования создает словарь с отдельными моделями и их количеством"""
    result = {}
    for item in data:
        try:
            result[item] += 1
        except KeyError:
            result[item] = 1
    return result


# def create_row_disk(disks: list, result: list, prices: dict, price_categor: dict):
#     disks_dict = count_equipment(disks)
#     for name, cnt in disks_dict.items():
#         row = [f"Модель {prices[name]['model']}\n{prices[name]['name']}",
#                'шт',
#                cnt,
#                f"{Decimal(prices[name]['price']).quantize(Decimal('.01'))}",
#                f"{(Decimal(prices[name]['price']) * cnt).quantize(Decimal('.01'))}"]
#         price_categor['total'] += (Decimal(prices[name]['price']) * cnt).quantize(Decimal('.01'))
#         price_categor['equipment'] += (Decimal(prices[name]['price']) * cnt).quantize(Decimal('.01'))
#         result.append(row)
#
#     return result, price_categor


def calculate_pipe(cams_out, cams_in, mt_cam):
    pipe_out = cams_out * mt_cam
    pipe_in = cams_in * mt_cam

    return pipe_out, pipe_in


def create_row_camera(id_tg, type_camera, count_camera, purpose, details_camera):
    total_price = (Decimal(details_camera[3].replace(',', '.')) * count_camera).quantize(Decimal('.01'))
    row = [
        f'{details_camera[-1]} {details_camera[0]} '
        f'{details_camera[1]}',
        'шт',
        count_camera,
        Decimal(details_camera[3].replace(',', '.')).quantize(Decimal('.01')),
        total_price
    ]

    return row, total_price


def check_switch(model, total_cam):
    recorder = db.get_data_equipments('DataRecorder', 'number_poe', {'model': model})[0]
    if recorder[0] >= int(total_cam):
        return False
    return True


def calculate_result(data, id_tg):
    c = Decimal('.01')
    price_of_categories = {'total': 0, 'equipment': 0, 'materials': 0, 'work': 0}
    result = list()
    to_provider = list()
    prices = parser_prices.open_prices()
    work = db.get_data_cost(id_tg, 'cost_work_analog') or db.get_data_cost(id_tg, 'cost_work')
    brand = data['data_cam_out'][-1] if 'data_cam_out' in data else data['data_cam_in'][-1]
    reg = Recorders(cams=int(data['total_cams']), archive=int(data['days_for_archive']), brand=brand, id_tg=id_tg,
                    system_ip=False)
    reg = reg.main()
    if not reg[0]:
        return False, reg[1]
    fasteners = calculate_fasteners(type_cam_in_room=data['type_cam_in_room'],
                                    type_cam_on_street=data['type_cam_on_street'],
                                    cams_in_room=int(data['cams_on_indoor']),
                                    cams_on_street=int(data['cams_on_street']))
    pipe_out, pipe_in = calculate_pipe(cams_in=int(data['cams_on_indoor']), cams_out=int(data['cams_on_street']),
                                       mt_cam=float(work[2]))
    result.append(['Оборудование'])
    if data['cams_on_indoor'] != '0':
        row_cam = create_row_camera(id_tg, data['type_cam_in_room'][2:], int(data['cams_on_indoor']), 'Внутренняя',
                                    data['data_cam_in'])
        result.append(row_cam[0])
        to_provider.append(row_cam[0][:3])
        price_of_categories['total'] += row_cam[1]
        price_of_categories['equipment'] += row_cam[1]
    if data['cams_on_street'] != '0':
        row_cam = create_row_camera(id_tg, data['type_cam_on_street'][2:], int(data['cams_on_street']), 'Уличная',
                                    data['data_cam_out'])
        result.append(row_cam[0])
        to_provider.append(row_cam[0][:3])
        price_of_categories['total'] += row_cam[1]
        price_of_categories['equipment'] += row_cam[1]
    rows_recorder_and_hdd = RowRecorderAndHDD(recorders=reg, id_tg=id_tg)
    rows_recorder_and_hdd = rows_recorder_and_hdd.main()
    for row in rows_recorder_and_hdd:
        price_of_categories['total'] += Decimal(row[-1]).quantize(Decimal('.01'))
        price_of_categories['equipment'] += Decimal(row[-1]).quantize(Decimal('.01'))
    result.extend(rows_recorder_and_hdd)
    to_provider.extend(i[:3] for i in rows_recorder_and_hdd)
    ibp = row_other.Ibp(total_cam=int(data['total_cams']), id_tg=id_tg).create_row()
    price_of_categories['total'] += Decimal(ibp[0][-1]).quantize(c)
    price_of_categories['equipment'] += Decimal(ibp[0][-1]).quantize(c)
    result.extend(ibp)
    to_provider.extend(i[:3] for i in ibp)
    locker = Locker(len(reg), None, reg[0][0].box, id_tg)
    row_locker = locker.main()
    for row in row_locker:
        price_of_categories['total'] += Decimal(row[-1]).quantize(Decimal('.01'))
        price_of_categories['equipment'] += Decimal(row[-1]).quantize(Decimal('.01'))
    result.extend(row_locker)
    to_provider.extend(i[:3] for i in row_locker)
    for key, value in fasteners.items():
        if value != 0:
            row = [f"Модель {prices[key]['model']} {prices[key]['name']}",
                   'шт',
                   value,
                   f"{Decimal(prices[key]['price']).quantize(c)}",
                   f"{(Decimal(prices[key]['price']) * int(value)).quantize(c)}"]
            price_of_categories['total'] += (Decimal(prices[key]['price']) * int(value)).quantize(c)
            price_of_categories['materials'] += (Decimal(prices[key]['price']) * int(value)).quantize(c)
            result.append(row)
            to_provider.append(row[:3])
    row = ['Материалы']
    result.append(row)
    to_provider.append(row)
    if reg[0][0].box == 0:
        row = locker.create_row_dsk()
        result.append(row)
    row = ['Монтажный комплект',
           'шт',
           data['total_cams'],
           f"{float(work[3]):.2f}",
           f"{(int(data['total_cams']) * Decimal(work[3])).quantize(c)}"]
    price_of_categories['total'] += (int(data['total_cams']) * Decimal(work[3])).quantize(c)
    price_of_categories['materials'] += (int(data['total_cams']) * Decimal(work[3])).quantize(c)
    result.append(row)
    box = row_other.Box(
        data['cams_on_indoor'],
        data['cams_on_street'],
        data['data_cam_in'][-2] if 'data_cam_in' in data else None,
        data['data_cam_out'][-2] if 'data_cam_out' in data else None
    )
    row_box = box.create_row()
    for row in row_box:
        price_of_categories['total'] += Decimal(row[-1]).quantize(Decimal('.01'))
        price_of_categories['materials'] += Decimal(row[-1]).quantize(Decimal('.01'))
    result.extend(row_box)
    cable = row_other.Cable(pipe_in, pipe_out, id_tg).create_row()
    for row in cable:
        price_of_categories['total'] += Decimal(row[-1]).quantize(Decimal('.01'))
        price_of_categories['materials'] += Decimal(row[-1]).quantize(Decimal('.01'))
    result.extend(cable)
    to_provider.extend(i[:3] for i in cable)
    pipe = row_other.Pipe(pipe_in, pipe_out, id_tg).create_row()
    for row in pipe:
        price_of_categories['total'] += Decimal(row[-1]).quantize(Decimal('.01'))
        price_of_categories['materials'] += Decimal(row[-1]).quantize(Decimal('.01'))
    result.extend(pipe)
    to_provider.extend(i[:3] for i in pipe)
    result.append(['Работа и настройка оборудования'])
    row = ['Монтаж камеры',
           'шт',
           data['total_cams'],
           f"{float(work[0]):.2f}",
           f"{(int(data['total_cams']) * Decimal(work[0])).quantize(c)}"]
    price_of_categories['total'] += (int(data['total_cams']) * Decimal(work[0])).quantize(c)
    price_of_categories['work'] += (int(data['total_cams']) * Decimal(work[0])).quantize(c)
    result.append(row)
    row = ['Монтаж кабеля в гофрированной трубе',
           'м',
           float(work[2]) * int(data['total_cams']),
           f"{float(work[1]):.2f}",
           f"{(Decimal(work[2]) * int(data['total_cams']) * Decimal(work[1])).quantize(c)}"]
    price_of_categories['total'] += (Decimal(work[2]) * int(data['total_cams']) * Decimal(work[1])).quantize(c)
    price_of_categories['work'] += (Decimal(work[2]) * int(data['total_cams']) * Decimal(work[1])).quantize(c)
    result.append(row)
    row = ['Пуско-наладочные работы систем видеонаблюдения',
           'шт',
           data['total_cams'],
           f"{float(work[4]):.2f}",
           f"{(int(data['total_cams']) * Decimal(work[4])).quantize(c)}"]
    price_of_categories['total'] += (int(data['total_cams']) * Decimal(work[4])).quantize(c)
    price_of_categories['work'] += (int(data['total_cams']) * Decimal(work[4])).quantize(c)
    result.append(row)

    return result, price_of_categories, to_provider
