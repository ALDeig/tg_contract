from decimal import Decimal

import db
from commercial_proposal import parser_prices
# from commercial_proposal.recorder_and_hdd import Recorders, RowRecorderAndHDD
from commercial_proposal.analog_kp.recorder_and_hdd import Recorders, RowRecorderAndHDD
from commercial_proposal.row_switch import Switch, RowsSwitch
from commercial_proposal.analog_kp.row_locker import Locker
from commercial_proposal import row_other


class Kp:
    def __int__(self, data, id_tg):
        self.total_cams = data['total_cams']
        self.days_archive = data['days_for_archive']
        self.cams_indoor = data['cams_on_indoor']
        self.cams_outdoor = data['cams_on_street']
        self.data_cam_in = data['data_cam_in']
        self.data_cam_out = data['data_cam_out']
        self.id_tg = id_tg
        self.result = list()
        self.price_of_categories = {'total': 0, 'equipment': 0, 'materials': 0, 'work': 0}


# def calculate_registrar(total_cam: int, days_archive: int, result: list):
#     """Вычисляет количество регистраторов и какие именно нужны"""
#     if total_cam <= 4:
#         if days_archive > 35:
#             result.append({'number_channels': '8', 'number_hdd': '2'})  #rec8cam2d
#         else:
#             result.append({'number_channels': '4', 'number_hdd': '1'})  #rec4cam1d
#     elif total_cam <= 8:
#         if days_archive > 17:
#             result.append({'number_channels': '8', 'number_hdd': '2'})  #rec8cam2d
#         else:
#             result.append({'number_channels': '8', 'number_hdd': '1'})  #rec8cam1d
#     elif total_cam <= 16:
#         if days_archive > 8:
#             result.append({'number_channels': '16', 'number_hdd': '2'})  #rec16cam2d
#         else:
#             result.append({'number_channels': '16', 'number_hdd': '1'})  #rec16cam1d
#     else:
#         if days_archive <= 8:
#             result.append({'number_channels': '16', 'number_hdd': '1'})  #rec16cam1d
#         else:
#             result.append({'number_channels': '16', 'number_hdd': '2'})  #rec16cam2d
#         calculate_registrar(total_cam=total_cam - 16, days_archive=days_archive, result=result)
#     return result

# print(calculate_registrar(20, 20, list()))

# def calculate_registrar_new(total_cam: int, days_archive: int, result: list):
#     """Вычисляет количество регистраторов и какие именно нужны"""
#     need_memory = total_cam * 40 * days_archive / 1024
#     if total_cam <= 4:
#         if need_memory > 6:
#             result.append({'number_channels': '8', 'number_hdd': '2'})  #rec8cam2d
#         else:
#             result.append({'number_channels': '4', 'number_hdd': '1'})  #rec4cam1d
#     elif total_cam <= 8:
#         if need_memory > 6:
#             result.append({'number_channels': '8', 'number_hdd': '2'})  #rec8cam2d
#         else:
#             result.append({'number_channels': '8', 'number_hdd': '1'})  #rec8cam1d
#     elif total_cam <= 16:
#         if need_memory > 6:
#             result.append({'number_channels': '16', 'number_hdd': '2'})  #rec16cam2d
#         else:
#             result.append({'number_channels': '16', 'number_hdd': '1'})  #rec16cam1d
#     else:
#         if need_memory <= 6:
#             result.append({'number_channels': '16', 'number_hdd': '1'})  #rec16cam1d
#         else:
#             result.append({'number_channels': '16', 'number_hdd': '2'})  #rec16cam2d
#         calculate_registrar_new(total_cam=total_cam - 16, days_archive=days_archive, result=result)
#     return result

# print(calculate_registrar_new(20, 16.4, list()))
#
# def find_need_memory_size(cams_in: tuple, cams_out: tuple, days_archive: int) -> int:
#     # size_for_day = {2: 42.2, 4: 60}
#     memory_for_in = cams_in[0] * size_for_day[cams_in[1]] * days_archive / 1024
#     print(memory_for_in, size_for_day[cams_in[1]])
#     memory_for_out = cams_out[0] * size_for_day[cams_out[1]] * days_archive / 1024
#     print(memory_for_out, size_for_day[cams_out[1]])
#     return memory_for_out + memory_for_in
#
# print(find_need_memory_size((10, 2), (10, 2), 20))


# def calculate_disks(regs: list, cams: int, archive: int, ppi: int = 2):
#     """Вычисляет количество дисков и их объем. Возвращате False если архив слишком большой"""
#     disks = []
#     cnt = 1
#     for reg in regs:
#         if reg['number_hdd'] == '2':
#             if len(reg) == 10:
#                 if cnt == len(regs):
#                     num_cams = cams
#                 else:
#                     num_cams = 16
#                     cnt += 1
#                     cams -= 16
#                 hdd = num_cams * ppi * int(archive) / 1024
#                 disk_1 = '6tb'
#                 disk = find_hdd(hdd - 6, [])
#                 if len(disk) > 1:
#                     return False
#                 disks.append(disk_1)
#                 disks.append(disk[0])
#             else:
#                 if cnt == len(regs):
#                     num_cams = cams
#                 else:
#                     num_cams = int(reg[3])
#                     cnt += 1
#                     cams -= int(reg[3])
#                 hdd = num_cams * 42.2 * int(archive) / 1024
#                 disk = find_hdd(hdd / 2, [])
#                 if len(disk) > 1:
#                     return False
#                 disks.append(disk[0])
#                 disks.append(disk[0])
#         else:
#             if len(reg) == 10:
#                 if cnt == len(regs):
#                     num_cams = cams
#                 else:
#                     num_cams = 16
#                     cnt += 1
#                     cams -= 16
#                 hdd = num_cams * 42.2 * int(archive) / 1024
#                 disk = find_hdd(hdd, [])
#                 disks.append(disk[0])
#             else:
#                 if cnt == len(regs):
#                     num_cams = cams
#                 else:
#                     num_cams = int(reg[3])
#                     cnt += 1
#                     cams -= int(reg[3])
#                 hdd = num_cams * 42.2 * int(archive) / 1024
#                 disk = find_hdd(hdd, [])
#                 disks.append(disk[0])
#     return disks

# def calculate_disks_new(regs: list, cams_in: int, cams_out: int, archive: int):
#     """Вычисляет количество дисков и их объем. Возвращате False если архив слишком большой"""
#     disks = []
#     cnt = 1
#     for reg in regs:
#         if reg['number_hdd'] == '2':
#             if reg['number_channels'] == '16':
#                 if cnt == len(regs):
#                     num_cams = cams
#                 else:
#                     num_cams = 16
#                     cnt += 1
#                     cams -= 16
#                 hdd = num_cams * ppi * int(archive) / 1024
#                 disk_1 = '6'
#                 disk = find_hdd(hdd - 6, [])
#                 if len(disk) > 1:
#                     return False
#                 disks.append(disk_1)
#                 disks.append(disk[0])
#             else:
#                 if cnt == len(regs):
#                     num_cams = cams
#                 else:
#                     num_cams = int(reg[3])
#                     cnt += 1
#                     cams -= int(reg[3])
#                 hdd = num_cams * 42.2 * int(archive) / 1024
#                 disk = find_hdd(hdd / 2, [])
#                 if len(disk) > 1:
#                     return False
#                 disks.append(disk[0])
#                 disks.append(disk[0])
#         else:
#             if len(reg) == 10:
#                 if cnt == len(regs):
#                     num_cams = cams
#                 else:
#                     num_cams = 16
#                     cnt += 1
#                     cams -= 16
#                 hdd = num_cams * 42.2 * int(archive) / 1024
#                 disk = find_hdd(hdd, [])
#                 disks.append(disk[0])
#             else:
#                 if cnt == len(regs):
#                     num_cams = cams
#                 else:
#                     num_cams = int(reg[3])
#                     cnt += 1
#                     cams -= int(reg[3])
#                 hdd = num_cams * 42.2 * int(archive) / 1024
#                 disk = find_hdd(hdd, [])
#                 disks.append(disk[0])
#     return disks


# def calculate_switch(total_cam: int, result: list):
#     """Вычисляет количество коммутаторов и какие именно нужны"""
#     if total_cam <= 4:
#         result.append('switch4')
#     elif total_cam <= 8:
#         result.append('switch8')
#     elif total_cam <= 16:
#         result.append('switch16')
#     elif total_cam <= 24:
#         result.append('switch24')
#     else:
#         result.append('switch24')
#         calculate_switch(total_cam - 24, result)
#
#     return result


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


# def find_hdd(hdd_: float, result: list):
#     """Вспомогательная функция для вычисления жестких дисков"""
#     if hdd_ <= 1:
#         result.append('1')
#     elif hdd_ <= 2:
#         result.append('2')
#     elif hdd_ <= 3:
#         result.append('3')
#     elif hdd_ <= 4:
#         result.append('4')
#     elif hdd_ <= 6:
#         result.append('6')
#     else:
#         result.append('6tb')
#         find_hdd(hdd_ - 6, result)
#     return result


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


# def find_max_archive(disks, cams):
#     """Вычисляет максимальный архив для данного количества камер"""
#     all_memory = 0
#     for disk in disks:
#         all_memory += int(disk[0])
#     need_memory_one_day = int(cams) * 42.2
#     max_archive = int(all_memory * 1024 / need_memory_one_day)
#     return max_archive


# def find_disks_for_max_archive(reg, cams, archive):
#     """Вспомогательная функция для нахождения максимального архива"""
#     flg = False
#     while not flg:
#         flg = calculate_disks(reg, cams, archive)
#         archive = archive - 1
#
#     return flg


def calculate_pipe(cams_out, cams_in, mt_cam):
    pipe_out = cams_out * mt_cam
    pipe_in = cams_in * mt_cam

    return pipe_out, pipe_in


# def calculate_locker(reg):
#     lockers = {1: 'locker_1', 2: 'locker_2', 3: 'locker_3', 4: 'locker_4', 5: 'locker_5', 6: 'locker_6'}
#     try:
#         locker = lockers[reg]
#     except KeyError:
#         locker = 'locker_6'
#
#     return locker


def create_row_camera(id_tg, type_camera, count_camera, purpose, details_camera):
    # camera = db.get_model_camera_of_user(type_camera, purpose, id_tg)
    # print(camera)
    # if not camera:
    #     details_camera = db.get_price_of_camera(view_cam=type_camera, purpose=purpose, ppi='2')
    # else:
    #     details_camera = db.get_price_of_camera(camera[0])
    # print(details_camera)
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
    result = []
    to_provider = list()
    prices = parser_prices.open_prices()
    work = db.get_data_cost(id_tg, 'cost_work')
    brand = data['data_cam_out'][-1] if 'data_cam_out' in data else data['data_cam_in'][-1]
    reg = Recorders(cams=int(data['total_cams']), archive=int(data['days_for_archive']), brand=brand, id_tg=id_tg,
                    system_ip=True)
    reg = reg.main()
    print(reg)
    if not reg[0]:
        return False, reg[1]
    fasteners = calculate_fasteners(type_cam_in_room=data['type_cam_in_room'],
                                    type_cam_on_street=data['type_cam_on_street'],
                                    cams_in_room=int(data['cams_on_indoor']),
                                    cams_on_street=int(data['cams_on_street']))
    pipe_out, pipe_in = calculate_pipe(cams_in=int(data['cams_on_indoor']), cams_out=int(data['cams_on_street']),
                                       mt_cam=float(work[2]))

    # Оборудование
    result.append(['Оборудование'])
    if data['cams_on_indoor'] != '0':
        row_cam = create_row_camera(id_tg, data['type_cam_in_room'][2:], int(data['cams_on_indoor']), 'Внутренняя',
                                    data['data_cam_in'])
        result.append(row_cam[0])
        to_provider.append(row_cam[0][0:3])
        price_of_categories['total'] += row_cam[1]
        price_of_categories['equipment'] += row_cam[1]
    if data['cams_on_street'] != '0':
        row_cam = create_row_camera(id_tg, data['type_cam_on_street'][2:], int(data['cams_on_street']), 'Уличная',
                                    data['data_cam_out'])
        result.append(row_cam[0])
        to_provider.append(row_cam[0][0:3])
        price_of_categories['total'] += row_cam[1]
        price_of_categories['equipment'] += row_cam[1]
    rows_recorder_and_hdd = RowRecorderAndHDD(recorders=reg, id_tg=id_tg)
    rows_recorder_and_hdd = rows_recorder_and_hdd.main()
    for row in rows_recorder_and_hdd:
        price_of_categories['total'] += Decimal(row[-1]).quantize(Decimal('.01'))
        price_of_categories['equipment'] += Decimal(row[-1]).quantize(Decimal('.01'))
    result.extend(rows_recorder_and_hdd)
    to_provider.extend(i[0:3] for i in rows_recorder_and_hdd)
    check_switch_result = check_switch(reg[0][0][1], data['total_cams'])
    if check_switch_result:
        switch = Switch(int(data['total_cams']), brand)
        switch = switch.calculate_switch()
        rows_switch = RowsSwitch(switch, id_tg, brand).create_rows()
        for row in rows_switch:
            price_of_categories['total'] += Decimal(row[-1]).quantize(Decimal('.01'))
            price_of_categories['equipment'] += Decimal(row[-1]).quantize(Decimal('.01'))
        result.extend(rows_switch)
        to_provider.extend(i[0:3] for i in rows_switch)
    else:
        switch = None
    row = [f"{prices['cable_organizer']['model']} - Кабельный организатор",
           'шт',
           len(switch if switch else reg),
           f"{Decimal(prices['cable_organizer']['price'])}",
           f"{(Decimal(prices['cable_organizer']['price']) * len(switch if switch else reg)).quantize(c)}"]
    price_of_categories['total'] += (Decimal(prices['cable_organizer']['price']) * len(switch if switch else reg)).quantize(c)
    price_of_categories['equipment'] += (Decimal(prices['cable_organizer']['price']) * len(switch if switch else reg)).quantize(c)
    result.append(row)
    to_provider.append(row)
    ibp = row_other.Ibp(total_cam=int(data['total_cams']), id_tg=id_tg).create_row()
    price_of_categories['total'] += Decimal(ibp[0][-1]).quantize(c)
    price_of_categories['equipment'] += Decimal(ibp[0][-1]).quantize(c)
    result.extend(ibp)
    to_provider.extend(i[0:3] for i in ibp)
    locker = Locker(len(reg), len(switch) if switch else None, reg[0][0].box, id_tg)
    # locker = locker.calculate_box()
    # row_locker = RowBox(id_tg, locker)
    # row_locker = row_locker.create_rows()
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
    # Материалы

    row = ['Материалы']
    result.append(row)
    to_provider.append(row)
    row = ['Монтажный комплект',
           'шт',
           data['total_cams'],
           f"{float(work[3]):.2f}",
           f"{(int(data['total_cams']) * Decimal(work[3])).quantize(c)}"]
    price_of_categories['total'] += (int(data['total_cams']) * Decimal(work[3])).quantize(c)
    price_of_categories['materials'] += (int(data['total_cams']) * Decimal(work[3])).quantize(c)
    result.append(row)
    to_provider.append(row[:3])
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
    to_provider.extend(i[:3] for i in row_box)
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
    # Настройка и работа

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
