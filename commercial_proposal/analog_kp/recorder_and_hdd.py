from decimal import Decimal

from loguru import logger

import db


class Recorders:
    """
    Класс в котором создаются формируется словарь с регистраторами. В словаре для каждого регистратора указано
    количество каналов, жестких дисков и размер дисков.
    Если указан слишком большой архив, то функция main возвращает False.
    """

    def __init__(self, cams: int, archive: int, brand: str, id_tg: int, system_ip: bool):
        self.cams = cams
        self.archive = archive
        self.brand = brand
        self.id_tg = id_tg
        if system_ip:
            self.ip = '='
        else:
            self.ip = '!='
        self.result = list()

    def check_brand(self):
        result = db.get_types('brand', 'DataRecorder')
        if self.brand in result:
            return True
        return False

    def find_recorder_in_selected(self):
        result = list()
        channels = db.get_types('number_channels', 'ChoiceRecorder',
                                {'id_tg': ('=', self.id_tg), 'type_recorder': (self.ip, 'Сетевые (IP)')})
        channels_all = db.get_types('number_channels', 'DataRecorder',
                                    {'number_channels': ('>=', self.cams), 'type_recorder': (self.ip, 'Сетевые (IP)')})
        if not channels:
            return False
        number_channels = None
        for channel in channels:
            if self.cams <= channel:
                number_channels = channel
                break
        if not number_channels:
            return False
        if number_channels > channels_all[0]:
            return False
        model = db.get_types('model', 'ChoiceRecorder',
                             {'id_tg': ('=', self.id_tg), 'type_recorder': (self.ip, 'Сетевые (IP)'),
                              'number_channels': ('=', number_channels)})
        columns = 'number_hdd, model, box, max_size_hdd'
        recorder = db.get_data(columns, 'DataRecorder', {'model': ('=', model[0])})[0]
        hdd = self.find_hdd(recorder, self.cams)
        if hdd[0]:
            result.append([recorder, hdd])
            return result
        return False

    def find_hdd(self, recorder, cams):
        brand = db.get_data('brand', 'ChoiceHDD', {'id_tg': ['=', self.id_tg]})
        if brand:
            sizes_hdd = db.get_options('DataHDD', 'memory_size', {'brand': brand[0].brand,
                                                                  'memory_size': recorder.max_size_hdd}, '<=')
        else:
            sizes_hdd = db.get_options('DataHDD', 'memory_size', {'memory_size': recorder.max_size_hdd}, '<=')
        need_size = cams * 24 * self.archive / 1024
        hdd = None
        number_hdd = None
        for cnt in range(1, recorder[0] + 1):
            for size in sizes_hdd:
                if need_size / cnt <= size:
                    hdd = size
                    number_hdd = cnt
                    break
            if hdd and number_hdd:
                return hdd, number_hdd
        return False, sizes_hdd[-1]

    def find_recorder_with_brand(self, cams):
        records = list()
        columns = 'number_hdd, model, box, max_size_hdd'
        while True:
            channels = db.get_types('number_channels', 'DataRecorder',
                                    {'brand': ('=', self.brand),
                                     'number_channels': ('>=', cams),
                                     'type_recorder': (self.ip, 'Сетевые (IP)'),
                                     'number_poe': ('=', 0)},
                                    )
            logger.debug(channels)
            if not channels:
                channels = db.get_types('number_channels', 'DataRecorder',
                                        {'brand': ['=', self.brand],
                                         'type_recorder': [self.ip, 'Сетевые (IP)'], 'number_poe': ['=', 0]})
                channels.sort()
                logger.debug(f'Без фильтра количесва камер - {channels}')
                recorder = db.get_data(columns, 'DataRecorder',
                                       {
                                           'brand': ['=', self.brand],
                                           'number_channels': ['=', channels[-1]],
                                           'type_recorder': [self.ip, 'Сетевые (IP)'],
                                           'number_poe': ['=', 0]
                                       })
                logger.debug(recorder)
                hdd = self.find_hdd(recorder[0], channels[-1])
                if not hdd[0]:
                    return False, hdd[-1] * recorder[0].number_hdd * 1024 / 24 / channels[-1]
                cams -= channels[-1]
                records.append([recorder[0], hdd])
                continue

            number_channels = None
            channels.sort()
            for channel in channels:
                if cams <= channel:
                    number_channels = channel
                    break
            recorder = db.get_data(columns, 'DataRecorder',
                                   {'brand': ('=', self.brand),
                                    'number_channels': ('=', number_channels),
                                    'type_recorder': (self.ip, 'Сетевые (IP)'),
                                    'number_poe': ('=', 0)})
            hdd = self.find_hdd(recorder[0], cams)
            if not hdd[0]:
                return False, hdd[-1] * recorder[0].number_hdd * 1024 / 24 / cams
            records.append([recorder[0], hdd])
            break

        return records

    def find_recorder(self, cams):
        records = list()
        columns = 'number_hdd, model, box, max_size_hdd'
        while True:
            channels = db.get_types('number_channels', 'DataRecorder',
                                    {'number_channels': ['>=', cams],
                                     'type_recorder': [self.ip, 'Сетевые (IP)'],
                                     'number_poe': ['=', 0]})
            logger.debug(channels)
            if not channels:
                channels = db.get_types('number_channels', 'DataRecorder',
                                        {'type_recorder': [self.ip, 'Сетевые (IP)'], 'number_poe': ['=', 0]})
                channels.sort()
                recorder = db.get_data(columns, 'DataRecorder',
                                       {'number_channels': ['=', channels[-1]],
                                        'type_recorder': [self.ip, 'Сетевые (IP)'],
                                        'number_poe': ['=', 0]})
                hdd = self.find_hdd(recorder[0], channels[-1])
                if not hdd[0]:
                    return False, hdd[-1] * recorder[0][0] * 1024 / 24 / channels[-1]
                cams -= channels[-1]
                records.append([recorder[0], hdd])
                continue

            number_channels = None
            channels.sort()
            for channel in channels:
                if cams <= channel:
                    number_channels = channel
                    break
            recorder = db.get_data(columns, 'DataRecorder',
                                   {'number_channels': ['=', number_channels], 'type_recorder': [self.ip, 'Сетевые (IP)'],
                                    'number_poe': ['=', 0]})
            hdd = self.find_hdd(recorder[0], cams)
            if not hdd[0]:
                return False, hdd[-1] * recorder[0][0] * 1024 / 24 / cams
            records.append([recorder[0], hdd])
            break

        return records

    def main(self):
        recorder = self.find_recorder_in_selected()
        if not recorder:
            brand = self.check_brand()
            if brand:
                recorder = self.find_recorder_with_brand(self.cams)
            else:
                recorder = self.find_recorder(self.cams)
        if not recorder[0]:
            return False, recorder[1]
        return recorder


class RowRecorderAndHDD:
    """Класс создает строки с регистраторами и жесткими дисками для заполения КП"""

    def __init__(self, recorders: list, id_tg: int):
        self.recorders = recorders
        self.id_tg = id_tg
        self.result = list()

    @staticmethod
    def get_data_recorder(model):
        columns = 'model, price, brand, description'
        recorder = db.get_data_equipments('DataRecorder', columns, {'model': model})

        return recorder

    def create_dict_recorder(self):
        dict_rec = {}
        # print(self.recorders)
        logger.debug(self.recorders)
        for recorder in self.recorders:
            # print(recorder[0][1])
            if recorder[0][1] in dict_rec:
                dict_rec[recorder[0][1]] += 1
            else:
                dict_rec[recorder[0][1]] = 1
        return dict_rec

    def create_row_recorder(self):
        recorders = self.create_dict_recorder()
        for model, cnt in recorders.items():
            # print('Модель регистратора при создании строки для КП: ', model)
            data = self.get_data_recorder(model)[0]
            price = str(data[1]).replace(',', '.')
            row = [f"{data[2]} {data[0]} {data[-1]}",
                   'шт',
                   cnt,
                   f"{Decimal(price).quantize(Decimal('.01'))}",
                   f"{(Decimal(price) * cnt).quantize(Decimal('.01'))}"]
            self.result.append(row)
        return self.result

    def get_data_hdd(self, hdd):
        brand = db.select_choice_equipment('brand', {'id_tg': self.id_tg}, 'ChoiceHDD')
        columns = 'model, price, brand, description'
        if not brand:
            data = db.get_data_equipments('DataHDD', columns, {'memory_size': hdd[0]})
            return data
        data = db.get_data_equipments('DataHDD', columns, {'memory_size': hdd[0], 'brand': brand})
        return data

    def create_dict_hdd(self):
        disks = {}
        for hdd in self.recorders:
            if hdd[1] in disks:
                disks[hdd[1]] += hdd[1][1]
            else:
                disks[hdd[1]] = hdd[1][1]
        return disks

    def create_row_hdd(self):
        disks = self.create_dict_hdd()
        for model, cnt in disks.items():
            data = self.get_data_hdd(model)[0]
            price = str(data[1]).replace(',', '.')
            row = [f"{data[2]} {data[0]}\n{data[-1]}",
                   'шт',
                   cnt,
                   f"{Decimal(price).quantize(Decimal('.01'))}",
                   f"{(Decimal(price) * cnt).quantize(Decimal('.01'))}"]
            self.result.append(row)
        return self.result

    def main(self):
        self.create_row_recorder()
        self.create_row_hdd()
        return self.result
