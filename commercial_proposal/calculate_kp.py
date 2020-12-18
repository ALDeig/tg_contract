from decimal import Decimal

import db
from commercial_proposal import parser_prices


def calculate_registrar(total_cam: int, days_archive: int, result: list):
    """Вычисляет количество регистраторов и какие именно нужны"""
    if total_cam <= 4:
        if days_archive > 35:
            result.append('rec8cam2d')
        else:
            result.append('rec4cam1d')
    elif total_cam <= 8:
        if days_archive > 17:
            result.append('rec8cam2d')
        else:
            result.append('rec8cam1d')
    elif total_cam <= 16:
        if days_archive > 8:
            result.append('rec16cam2d')
        else:
            result.append('rec16cam1d')
    else:
        if days_archive <= 8:
            result.append('rec16cam1d')
        else:
            result.append('rec16cam2d')
        calculate_registrar(total_cam=total_cam - 16, days_archive=days_archive, result=result)
    return result


def calculate_disks(regs: list, cams: int, archive: int, ppi: int):
    """Вычисляет количество дисков и их объем. Возвращате False если архив слишком большой"""
    disks = []
    cnt = 1
    for reg in regs:
        if reg[-2] == '2':
            if len(reg) == 10:
                if cnt == len(regs):
                    num_cams = cams
                else:
                    num_cams = 16
                    cnt += 1
                    cams -= 16
                hdd = num_cams * ppi * int(archive) / 1024
                disk_1 = '6tb'
                disk = find_hdd(hdd - 6, [])
                if len(disk) > 1:
                    return False
                disks.append(disk_1)
                disks.append(disk[0])
            else:
                if cnt == len(regs):
                    num_cams = cams
                else:
                    num_cams = int(reg[3])
                    cnt += 1
                    cams -= int(reg[3])
                hdd = num_cams * 42.2 * int(archive) / 1024
                disk = find_hdd(hdd / 2, [])
                if len(disk) > 1:
                    return False
                disks.append(disk[0])
                disks.append(disk[0])
        else:
            if len(reg) == 10:
                if cnt == len(regs):
                    num_cams = cams
                else:
                    num_cams = 16
                    cnt += 1
                    cams -= 16
                hdd = num_cams * 42.2 * int(archive) / 1024
                disk = find_hdd(hdd, [])
                disks.append(disk[0])
            else:
                if cnt == len(regs):
                    num_cams = cams
                else:
                    num_cams = int(reg[3])
                    cnt += 1
                    cams -= int(reg[3])
                hdd = num_cams * 42.2 * int(archive) / 1024
                disk = find_hdd(hdd, [])
                disks.append(disk[0])
    return disks


def calculate_switch(total_cam: int, result: list):
    """Вычисляет количество коммутаторов и какие именно нужны"""
    if total_cam <= 4:
        result.append('switch4')
    elif total_cam <= 8:
        result.append('switch8')
    elif total_cam <= 16:
        result.append('switch16')
    elif total_cam <= 24:
        result.append('switch24')
    else:
        result.append('switch24')
        calculate_switch(total_cam - 24, result)

    return result


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


def find_hdd(hdd_: float, result: list):
    """Вспомогательная функция для вычисления жестких дисков"""
    if hdd_ <= 1:
        result.append('1tb')
    elif hdd_ <= 2:
        result.append('2tb')
    elif hdd_ <= 3:
        result.append('3tb')
    elif hdd_ <= 4:
        result.append('4tb')
    elif hdd_ <= 6:
        result.append('6tb')
    else:
        result.append('6tb')
        find_hdd(hdd_ - 6, result)
    return result


# def calculate_disk(total_cam, days_archive, num_reg):
#     hdd = int(total_cam) * 42.2 * int(days_archive) / 1024
#     hdd = hdd / num_reg
#     result = find_hdd(hdd, [])
#
#     return result


def calculate_meter(total_cam, mt_cam):
    """Вычисляет количество метров кабеля"""
    cctv_cable = total_cam * mt_cam

    return cctv_cable


def count_equipment(data: list) -> dict:
    result = {}
    for item in data:
        try:
            result[item] += 1
        except KeyError:
            result[item] = 1
    return result


def create_row_disk(disks: list, result: list, prices: dict, price_categor: dict):
    disks_dict = count_equipment(disks)
    for name, cnt in disks_dict.items():
        row = [f"Модель {prices[name]['model']}\n{prices[name]['name']}",
               'шт',
               cnt,
               f"{Decimal(prices[name]['price']).quantize(Decimal('.01'))}",
               f"{(Decimal(prices[name]['price']) * cnt).quantize(Decimal('.01'))}"]
        price_categor['total'] += (Decimal(prices[name]['price']) * cnt).quantize(Decimal('.01'))
        price_categor['equipment'] += (Decimal(prices[name]['price']) * cnt).quantize(Decimal('.01'))
        result.append(row)

    return result, price_categor


def find_max_archive(disks, cams):
    """Вычисляет максимальный архив для данного количества камер"""
    all_memory = 0
    for disk in disks:
        all_memory += int(disk[0])
    need_memory_one_day = int(cams) * 42.2
    max_archive = int(all_memory * 1024 / need_memory_one_day)
    return max_archive


def find_disks_for_max_archive(reg, cams, archive):
    """Вспомогательная функция для нахождения максимального архива"""
    flg = False
    while not flg:
        flg = calculate_disks(reg, cams, archive)
        archive = archive - 1

    return flg


def calculate_pipe(cams_out, cams_in, mt_cam):
    pipe_out = cams_out * mt_cam
    pipe_in = cams_in * mt_cam

    return pipe_out, pipe_in


def calculate_locker(reg):
    lockers = {1: 'locker_1', 2: 'locker_2', 3: 'locker_3', 4: 'locker_4', 5: 'locker_5', 6: 'locker_6'}
    try:
        locker = lockers[reg]
    except KeyError:
        locker = 'locker_6'

    return locker


def create_row_camera(id_tg, type_camera, count_camera):
    camera = db.get_model_camera_of_user(type_camera, id_tg)
    if not camera:
        return False
    details_camera = db.get_price_of_camera(camera)
    total_price = (Decimal(details_camera[3]) * count_camera).quantize(Decimal('.01'))
    row = [
        f'Модель: {details_camera[0]}\n'
        f'{details_camera[1]}',
        'шт',
        count_camera,
        Decimal(details_camera[3]).quantize(Decimal('.01')),
        total_price
    ]

    return row, total_price


def calculate_result(data, id_tg):
    c = Decimal('.01')
    price_of_categories = {'total': 0, 'equipment': 0, 'materials': 0, 'work': 0}
    type_cams = {'🔘 Купольная': 'dome_cam', '🔘 Цилиндрическая': 'cylindrical_cam', '🔘 Компактная': 'compact_cam'}
    type_cam = {'🔘 Купольная': 'cup', '🔘 Цилиндрическая': 'cyl', '🔘 Компактная': 'com'}
    result = []
    prices = parser_prices.open_prices()
    work = db.get_data_cost(id_tg)
    reg = calculate_registrar(total_cam=int(data['total_cams']), days_archive=int(data['days_for_archive']), result=[])
    camera = db.get_model_camera_of_user(type_cam[data['type_cam_in_room'] or data['type_cam_on_street']], id_tg)
    if not camera or db.get_price_of_camera(camera)[4] == '2':
        ppi = 42.2
    else:
        ppi = 60
    hdd = calculate_disks(regs=reg, cams=int(data['total_cams']), archive=data['days_for_archive'], ppi=ppi)
    if not hdd:
        disks = find_disks_for_max_archive(reg, int(data['total_cams']), int(data['days_for_archive']))
        max_archive = find_max_archive(disks, data['total_cams'])
        return False, max_archive
    switch = calculate_switch(total_cam=int(data['total_cams']), result=[])
    fasteners = calculate_fasteners(type_cam_in_room=data['type_cam_in_room'],
                                    type_cam_on_street=data['type_cam_on_street'],
                                    cams_in_room=int(data['cams_on_indoor']),
                                    cams_on_street=int(data['cams_on_street']))
    cable = calculate_meter(total_cam=int(data['total_cams']), mt_cam=int(work[2]))
    pipe_out, pipe_in = calculate_pipe(cams_in=int(data['cams_on_indoor']), cams_out=int(data['cams_on_street']),
                                       mt_cam=int(work[2]))
    locker = calculate_locker(len(reg))
    result.append(['Оборудование'])
    if data['cams_on_indoor'] != '0':
        row_cam = create_row_camera(id_tg, type_cam[data['type_cam_in_room']], int(data['cams_on_indoor']))
        if not row_cam:
            total_price = (int(data['cams_on_indoor']) * Decimal(
                prices[type_cams[data['type_cam_in_room']]]['price'])).quantize(c)
            price_of_categories['total'] += total_price
            price_of_categories['equipment'] += total_price
            row = [f"Модель: {prices[type_cams[data['type_cam_in_room']]]['model']}\n"
                   f"{prices[type_cams[data['type_cam_in_room']]]['name']}",
                   'шт',
                   data['cams_on_indoor'],
                   f"{float(prices[type_cams[data['type_cam_in_room']]]['price']):.2f}",
                   f"{total_price}"]
            result.append(row)
        else:
            result.append(row_cam[0])
            price_of_categories['total'] += row_cam[1]
            price_of_categories['equipment'] += row_cam[1]
    if data['cams_on_street'] != '0':
        row_cam = create_row_camera(id_tg, type_cam[data['type_cam_on_street']], int(data['cams_on_street']))
        if not row_cam:
            total_price = (int(data['cams_on_street']) * Decimal(
                prices[type_cams[data['type_cam_on_street']]]['price'])).quantize(c)
            price_of_categories['total'] += total_price
            price_of_categories['equipment'] += total_price
            row = [f"Модель {prices[type_cams[data['type_cam_on_street']]]['model']}\n"
                   f"{prices[type_cams[data['type_cam_on_street']]]['name']}",
                   'шт',
                   data['cams_on_street'],
                   f"{float(prices[type_cams[data['type_cam_on_street']]]['price']):.2f}",
                   f"{total_price}"]
            result.append(row)
        else:
            result.append(row_cam[0])
            price_of_categories['total'] += row_cam[1]
            price_of_categories['equipment'] += row_cam[1]
    result, price_of_categories = create_row_disk(reg, result, prices, price_of_categories)
    result, price_of_categories = create_row_disk(hdd, result, prices, price_of_categories)
    result, price_of_categories = create_row_disk(switch, result, prices, price_of_categories)
    row = [f"Модель {prices['cable_organizer']['model']} - Кабельный организатор",
           'шт',
           len(switch),
           f"{Decimal(prices['cable_organizer']['price'])}",
           f"{(Decimal(prices['cable_organizer']['price']) * len(switch)).quantize(c)}"]
    price_of_categories['total'] += (Decimal(prices['cable_organizer']['price']) * len(switch)).quantize(c)
    price_of_categories['equipment'] += (Decimal(prices['cable_organizer']['price']) * len(switch)).quantize(c)
    result.append(row)

    if int(data['total_cams']) <= 16:
        ibp = 'ibp_16'
    else:
        ibp = 'ibp_17'
    row = [f"Модель {prices[ibp]['model']} {prices[ibp]['name']} - ИБП",
           'шт',
           1,
           f"{Decimal(prices[ibp]['price'])}",
           f"{Decimal(prices[ibp]['price']).quantize(c)}"]
    price_of_categories['total'] += Decimal(prices[ibp]['price']).quantize(c)
    price_of_categories['equipment'] += Decimal(prices[ibp]['price']).quantize(c)
    result.append(row)
    if locker == 'locker_6':
        name_lock = 'Шкаф напольный'
    else:
        name_lock = 'Шкаф настенный'
    row = [f"Модель {prices[locker]['model']} {prices[locker]['name']} - {name_lock}",
           'шт',
           1,
           f"{Decimal(prices[locker]['price']).quantize(c)}",
           f"{Decimal(prices[locker]['price']).quantize(c)}"]
    price_of_categories['total'] += Decimal(prices[locker]['price']).quantize(c)
    price_of_categories['equipment'] += Decimal(prices[locker]['price']).quantize(c)
    result.append(row)

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
    row = ['Материалы']
    result.append(row)
    row = ['Монтажный комплект',
           'шт',
           data['total_cams'],
           f"{float(work[3]):.2f}",
           f"{(int(data['total_cams']) * Decimal(work[3])).quantize(c)}"]
    price_of_categories['total'] += (int(data['total_cams']) * Decimal(work[3])).quantize(c)
    price_of_categories['materials'] += (int(data['total_cams']) * Decimal(work[3])).quantize(c)
    result.append(row)
    price_cable = Decimal(prices['cctv_cable']['price']) / 305
    row = [f"Модель {prices['cctv_cable']['model']} {prices['cctv_cable']['name']}",
           'м',
           cable,
           f"{float(price_cable):.2f}",
           f"{(price_cable * Decimal(cable)).quantize(c)}"]
    price_of_categories['total'] += (price_cable * Decimal(cable)).quantize(c)
    price_of_categories['materials'] += (price_cable * Decimal(cable)).quantize(c)
    result.append(row)
    if pipe_in != 0:
        row = [f"Модель {prices['corrugated_pipe']['model']} {prices['corrugated_pipe']['name']}",
               'м',
               pipe_in,
               f"{Decimal(prices['corrugated_pipe']['price']).quantize(c)}",
               f"{(Decimal(prices['corrugated_pipe']['price']) * pipe_in).quantize(c)}"]
        price_of_categories['total'] += (Decimal(prices['corrugated_pipe']['price']) * pipe_in).quantize(c)
        price_of_categories['materials'] += (Decimal(prices['corrugated_pipe']['price']) * pipe_in).quantize(c)
        result.append(row)
    if pipe_out != 0:
        row = [f"Модель {prices['corrugated_pipe_out']['model']} {prices['corrugated_pipe_out']['name']}",
               'м',
               pipe_out,
               f"{Decimal(prices['corrugated_pipe_out']['price']).quantize(c)}",
               f"{(Decimal(prices['corrugated_pipe_out']['price']) * pipe_out).quantize(c)}"]
        price_of_categories['total'] += (Decimal(prices['corrugated_pipe_out']['price']) * pipe_out).quantize(c)
        price_of_categories['materials'] += (Decimal(prices['corrugated_pipe_out']['price']) * pipe_out).quantize(c)
        result.append(row)
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

    return result, price_of_categories
