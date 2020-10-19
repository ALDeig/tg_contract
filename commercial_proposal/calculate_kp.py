import db
from commercial_proposal import parser_prices


def calculate_registrar(total_cam: int, days_archive: int, result: list):
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
    # print(result дн.)
    return result


def calculate_disks(regs: list, cams: int, archive: int):
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
                hdd = num_cams * 42.2 * int(archive) / 1024
                disk_1 = '6tb'  # здесь сделать изменения
                disk = find_hdd(hdd - 6, [])
                if len(disk) > 1:
                    return False
                disks.append(disk_1)
                disks.append(disk[0])
                # disks.append(disk[-1])
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
                # disks.append(disk[-1])
                # disks.append(disk[-1])
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
                # disks.append(disk[-1])
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
                # disks.append(disk[-1])
    return disks


def calculate_switch(total_cam: int, result: list):
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
    # print(result)
    return result


def calculate_disk(total_cam, days_archive, num_reg):
    hdd = int(total_cam) * 42.2 * int(days_archive) / 1024
    # тест
    hdd = hdd / num_reg
    result = find_hdd(hdd, [])

    return result


def calculate_meter(total_cam, mt_cam):
    cctv_cable = total_cam * mt_cam

    return cctv_cable


def count_disks(disks: list):
    result = {}
    for disk in disks:
        try:
            result[disk] += 1
        except KeyError:
            result[disk] = 1
    return result


def create_row_disk(disks: list, result: list, prices: dict, price_categor: dict):
    disks_dict = count_disks(disks)
    for name, cnt in disks_dict.items():
        row = [f"Модель {prices[name]['model']}\n{prices[name]['name']}",
               'шт',
               cnt,
               f"{float(prices[name]['price']):.2f}",
               f"{float(prices[name]['price']) * cnt:.2f}"]
        price_categor['total'] += float(prices[name]['price']) * cnt
        price_categor['equipment'] += float(prices[name]['price']) * cnt
        result.append(row)

    return result, price_categor


def create_row_reg(regs: list, result: list, prices: dict, price_categories: dict) -> tuple:
    if len(regs) == 1:
        row = [f"Модель {prices[regs[0]]['model']}\n{prices[regs[0]]['name']}",
               'шт',
               '1',
               f"{float(prices[regs[0]]['price']):.2f}",
               f"{float(prices[regs[0]]['price']):.2f}"]
        result.append(row)
        price_categories['total'] += float(prices[regs[0]]['price'])
        price_categories['equipment'] += float(prices[regs[0]]['price'])
    else:
        if regs[0] == regs[-1]:
            row = [f"Модель {prices[regs[0]]['model']}\n{prices[regs[0]]['name']}",
                   'шт',
                   f'{len(regs)}',
                   f"{float(prices[regs[0]]['price']):.2f}",
                   f"{float(prices[regs[0]]['price']) * len(regs):.2f}"]
            result.append(row)
            price_categories['total'] += float(prices[regs[0]]['price']) * len(regs)
            price_categories['equipment'] += float(prices[regs[0]]['price']) * len(regs)
        else:
            row = [f"Модель {prices[regs[0]]['model']}\n{prices[regs[0]]['name']}",
                   'шт',
                   f"{len(regs) - 1}",
                   f"{float(prices[regs[0]]['price']):.2f}",
                   f"{float(prices[regs[0]]['price']) * (len(regs) - 1):.2f}"]
            result.append(row)
            price_categories['total'] += float(prices[regs[0]]['price']) * len(regs) - 1
            price_categories['equipment'] += float(prices[regs[0]]['price']) * len(regs) - 1
            row = [f"Модель {prices[regs[-1]]['model']}\n{prices[regs[-1]]['name']}",
                   'шт',
                   '1',
                   f"{float(prices[regs[-1]]['price']):.2f}",
                   f"{float(prices[regs[-1]]['price']):.2f}"]
            result.append(row)
            price_categories['total'] += float(prices[regs[-1]]['price'])
            price_categories['equipment'] += float(prices[regs[-1]]['price'])

    return result, price_categories


def create_row_switch(switch: list, result: list, prices: dict, price_categories: dict):
    if len(switch) == 1:
        row = [f"Модель {prices[switch[0]]['model']}\n{prices[switch[0]]['name']}",
               'шт',
               '1',
               f"{float(prices[switch[0]]['price']):.2f}",
               f"{float(prices[switch[0]]['price']):.2f}"]
        result.append(row)
        price_categories['total'] += float(prices[switch[0]]['price'])
        price_categories['equipment'] += float(prices[switch[0]]['price'])
    else:
        if switch[0] == switch[-1]:
            row = [f"Модель {prices[switch[0]]['model']}\n{prices[switch[0]]['name']}",
                   'шт',
                   f'{len(switch)}',
                   f"{float(prices[switch[0]]['price']):.2f}",
                   f"{float(prices[switch[0]]['price']) * len(switch):.2f}"]
            result.append(row)
            price_categories['total'] += float(prices[switch[0]]['price']) * len(switch)
            price_categories['equipment'] += float(prices[switch[0]]['price']) * len(switch)
        else:
            row = [f"Модель {prices[switch[0]]['model']}\n{prices[switch[0]]['name']}",
                   'шт',
                   f'{len(switch) - 1}',
                   f"{float(prices[switch[0]]['price']):.2f}",
                   f"{float(prices[switch[0]]['price']) * (len(switch) - 1):.2f}"]
            result.append(row)
            price_categories['total'] += float(prices[switch[0]]['price']) * len(switch) - 1
            price_categories['equipment'] += float(prices[switch[0]]['price']) * len(switch) - 1
            row = [f"Модель {prices[switch[-1]]['model']}\n{prices[switch[-1]]['name']}",
                   'шт',
                   '1',
                   f"{float(prices[switch[-1]]['price']):.2f}",
                   f"{float(prices[switch[-1]]['price']):.2f}"]
            result.append(row)
            price_categories['total'] += float(prices[switch[-1]]['price'])
            price_categories['equipment'] += float(prices[switch[-1]]['price'])

    return result, price_categories


def find_max_archive(disks, cams, archive):
    all_memory = 0
    # print(disks)
    # print(f'cams: {cams}, archive: {archive}')
    for disk in disks:
        all_memory += int(disk[0])
    need_memory_one_day = int(cams) * 42.2
    max_archive = int(all_memory * 1024 / need_memory_one_day)
    # if int(archive) > max_archive:
    return max_archive


def find_disks_for_max_archive(reg, cams, archive):
    flg = False
    while not flg:
        flg = calculate_disks(reg, cams, archive)
        archive = archive - 1

    return flg


def calculate_result(data, id_tg):
    price_of_categories = {'total': 0, 'equipment': 0, 'materials': 0, 'work': 0}
    type_cams = {'Купольная': 'dome_cam', 'Цилиндрическая': 'cylindrical_cam', 'Компактная': 'compact_cam'}
    result = []
    prices = parser_prices.open_prices()
    work = db.get_data_cost(id_tg)
    reg = calculate_registrar(total_cam=int(data['total_cams']), days_archive=int(data['days_for_archive']), result=[])
    hdd = calculate_disks(regs=reg, cams=int(data['total_cams']), archive=data['days_for_archive'])
    if not hdd:
        disks = find_disks_for_max_archive(reg, int(data['total_cams']), int(data['days_for_archive']))
        max_archive = find_max_archive(disks, data['total_cams'], data['days_for_archive'])
        return False, max_archive
    # check_archive = find_max_archive(hdd, data['total_cams'], data['days_for_archive'])
    # if check_archive:
    #     return False, check_archive
    switch = calculate_switch(total_cam=int(data['total_cams']), result=[])
    fasteners = calculate_fasteners(type_cam_in_room=data['type_cam_in_room'],
                                    type_cam_on_street=data['type_cam_on_street'],
                                    cams_in_room=int(data['cams_on_indoor']),
                                    cams_on_street=int(data['cams_on_street']))
    # hdd = calculate_disk(total_cam=int(data['total_cams']), days_archive=int(data['days_for_archive']), num_reg=len(reg))
    # hdd = calculate_disks(regs=reg, cams=int(data['total_cams']), archive=data['days_for_archive'])
    # if not hdd:
    #     return False
    cable = calculate_meter(total_cam=int(data['total_cams']), mt_cam=int(work[2]))
    result.append(['Оборудование'])
    if data['cams_on_indoor'] != '0':
        total_price = int(data['cams_on_indoor']) * float(prices[type_cams[data['type_cam_in_room']]]['price'])
        price_of_categories['total'] += float(total_price)
        price_of_categories['equipment'] += float(total_price)
        row = [f"Модель: {prices[type_cams[data['type_cam_in_room']]]['model']}\n"
               f"{prices[type_cams[data['type_cam_in_room']]]['name']}",
               'шт',
               data['cams_on_indoor'],
               f"{float(prices[type_cams[data['type_cam_in_room']]]['price']):.2f}",
               f"{float(int(data['cams_on_indoor']) * float(prices[type_cams[data['type_cam_in_room']]]['price'])):.2f}"]
        result.append(row)
    if data['cams_on_street'] != '0':
        total_price = int(data['cams_on_street']) * int(prices[type_cams[data['type_cam_on_street']]]['price'])
        price_of_categories['total'] += float(total_price)
        price_of_categories['equipment'] += float(total_price)
        row = [f"Модель {prices[type_cams[data['type_cam_on_street']]]['model']}\n"
               f"{prices[type_cams[data['type_cam_on_street']]]['name']}",
               'шт',
               data['cams_on_street'],
               f"{float(prices[type_cams[data['type_cam_on_street']]]['price']):.2f}",
               f"{float(int(data['cams_on_street']) * int(prices[type_cams[data['type_cam_on_street']]]['price'])):.2f}"]
        result.append(row)
    # for regist in reg:
    #     row = [f"Модель {prices[regist]['model']}\n{prices[regist]['name']}",
    #            'шт',
    #            '1',
    #            f"{float(prices[regist]['price']):.2f}",
    #            f"{float(prices[regist]['price']):.2f}"]
    #     price_of_categories['total'] += float(prices[regist]['price'])
    #     price_of_categories['equipment'] += float(prices[regist]['price'])
    #     result.append(row)
    # for disk in hdd:
    #     row = [f"Модель {prices[disk]['model']}\n{prices[disk]['name']}",
    #            'шт',
    #            '1',
    #            f"{float(prices[disk]['price']):.2f}",
    #            f"{float(prices[disk]['price']):.2f}"]
    #     price_of_categories['total'] += float(prices[disk]['price'])
    #     price_of_categories['equipment'] += float(prices[disk]['price'])
    #     result.append(row)
    result, price_of_categories = create_row_reg(reg, result, prices, price_of_categories)
    result, price_of_categories = create_row_disk(hdd, result, prices, price_of_categories)
    result, price_of_categories = create_row_switch(switch, result, prices, price_of_categories)
    # for switch_1 in switch:
    #     row = [f"Модель {prices[switch_1]['model']}\n{prices[switch_1]['name']}",
    #            'шт',
    #            '1',
    #            f"{float(prices[switch_1]['price']):.2f}",
    #            f"{float(prices[switch_1]['price']):.2f}"]
    #     price_of_categories['total'] += float(prices[switch_1]['price'])
    #     price_of_categories['equipment'] += float(prices[switch_1]['price'])
    #     result.append(row)
    for key, value in fasteners.items():
        if value != 0:
            row = [f"Модель {prices[key]['model']} {prices[key]['name']}",
                   'шт',
                   value,
                   f"{float(prices[key]['price']):.2f}",
                   f"{float(prices[key]['price']) * int(value):.2f}"]
            price_of_categories['total'] += float(prices[key]['price']) * int(value)
            price_of_categories['materials'] += float(prices[key]['price']) * int(value)
            result.append(row)
    row = ['Материалы']
    result.append(row)
    row = ['Монтажный комплект',
           'шт',
           data['total_cams'],
           f"{float(work[3]):.2f}",
           f"{(int(data['total_cams']) * int(work[3])):.2f}"]
    price_of_categories['total'] += int(data['total_cams']) * int(work[3])
    price_of_categories['materials'] += int(data['total_cams']) * int(work[3])
    result.append(row)
    # второй в матиралах
    price_cable = float(prices['cctv_cable']['price']) / 305
    row = [f"Модель {prices['cctv_cable']['model']}\n{prices['cctv_cable']['name']}",
           'м',
           cable,
           f"{float(price_cable):.2f}",
           f"{(price_cable * float(cable)):.2f}"]
    price_of_categories['total'] += float(prices['cctv_cable']['price'])
    price_of_categories['materials'] += float(prices['cctv_cable']['price'])
    result.append(row)
    row = [f"Модель {prices['corrugated_pipe']['model']} {prices['corrugated_pipe']['name']}",
           'м',
           cable,
           f"{float(prices['corrugated_pipe']['price']):.2f}",
           f"{(float(prices['corrugated_pipe']['price']) * float(cable)):.2f}"]
    price_of_categories['total'] += float(prices['corrugated_pipe']['price']) * float(cable)
    price_of_categories['materials'] += float(prices['corrugated_pipe']['price']) * float(cable)
    result.append(row)
    result.append(['Работа и настройка оборудования'])
    row = ['Монтаж камеры',
           'шт',
           data['total_cams'],
           f"{float(work[0]):.2f}",  # Здесь продолжить
           f"{(int(data['total_cams']) * float(work[0])):.2f}"]
    price_of_categories['total'] += int(data['total_cams']) * float(work[0])
    price_of_categories['work'] += int(data['total_cams']) * float(work[0])
    result.append(row)
    row = ['Монтаж кабеля в гофрированной трубе',
           'м',
           float(work[2]) * int(data['total_cams']),
           f"{float(work[1]):.2f}",
           f"{(float(work[2]) * int(data['total_cams']) * float(work[1])):.2f}"]
    price_of_categories['total'] += float(work[2]) * int(data['total_cams']) * float(work[1])
    price_of_categories['work'] += float(work[2]) * int(data['total_cams']) * float(work[1])
    result.append(row)
    row = ['Пуско-наладочные работы систем видеонаблюдения',
           'шт',
           data['total_cams'],
           f"{float(work[4]):.2f}",
           f"{(int(data['total_cams']) * float(work[4])):.2f}"]
    price_of_categories['total'] += int(data['total_cams']) * float(work[4])
    price_of_categories['work'] += int(data['total_cams']) * float(work[4])
    result.append(row)

    return result, price_of_categories

# dome_cam', 'cylindrical_cam', 'compact_cam', 'rec4cam1d', 'rec8cam1d', 'rec8cam2d', 'rec16cam1d',
#                    'rec16cam2d', 'switch4', 'switch8', 'switch16', 'switch24', 'bracket_dome', 'bracket_cyl',
#                    'cctv_cable
