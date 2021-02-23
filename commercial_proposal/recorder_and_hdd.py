from decimal import Decimal

import db


class Recorders:
    """
    Класс в котором создаются формируется словарь с регистраторами. В словаре для каждого регистратора указано
    количество каналов, жестких дисков и размер дисков.
    Если указан слишком большой архив, то функция main возвращает False.
    """

    def __init__(self, cams: int, archive: int, brand: str, id_tg: int):
        self.cams = cams
        self.archive = archive
        self.brand = brand
        self.id_tg = id_tg
        self.result = list()

    def check_brand(self):
        result = db.get_options('DataRecorder', 'brand')
        if self.brand in result:
            return True
        return False

    def find_recorder_in_selected(self):
        result = list()
        channels = db.get_options('ChoiceRecorder', 'number_channels', {'id_tg': self.id_tg}, '=')
        channels_all = db.get_options('DataRecorder', 'number_channels', {'number_channels': self.cams}, '>=')
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
        model = db.select_choice_equipment('model',
                                           {'id_tg': self.id_tg, 'number_channels': number_channels},
                                           'ChoiceRecorder')
        columns = 'number_hdd, model, max_size_hdd'
        recorder = db.get_data_equipments('DataRecorder', columns, {'model': model})
        hdd = self.find_hdd(recorder[0], self.cams)
        if hdd[0]:
            result.append([recorder[0], hdd])
            return result
        return False

    def find_hdd(self, recorder, cams):
        brand = db.select_choice_equipment('brand', {'id_tg': self.id_tg}, 'ChoiceHDD')
        if brand:
            sizes_hdd = db.get_options('DataHDD', 'memory_size', {'brand': brand, 'memory_size': recorder[-1]}, '<=')
        else:
            sizes_hdd = db.get_options('DataHDD', 'memory_size', {'memory_size': recorder[-1]}, '<=')
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

    # @staticmethod
    # def find_recorder_channels_with_brand(brand, cams=None):
    #     """
    #     Функция находит все варинты количества каналов в регистраторе больше или равного количесвку камер. Если та
    #     кого регистратора нет, то берет все варианты количества каналов.
    #     """
    #     if not cams:
    #         recorder_channels = db.get_recorder_channels_with_brand(brand=brand)
    #     else:
    #         recorder_channels = db.get_recorder_channels_with_brand(brand=brand, number_channels=cams)
    #     return recorder_channels

    # @staticmethod
    # def find_recorder_channels(cams=None):
    #     """
    #     Функция находит все варинты количества каналов в регистраторе больше или равного количесвку камер. Если та
    #     кого регистратора нет, то берет все варианты количества каналов.
    #     """
    #     if not cams:
    #         recorder_channels = db.get_recorder_channels()
    #     else:
    #         recorder_channels = db.get_recorder_channels(number_channels=cams)
    #     return recorder_channels

    def find_recorder_with_brand(self, cams):
        records = list()
        columns = 'number_hdd, model, max_size_hdd'
        while True:
            channels = db.get_options('DataRecorder', 'number_channels',
                                      {'brand': self.brand, 'number_channels': cams, 'type_recorder': 'Сетевые (IP)', 'number_poe': 0},
                                      '>=')
            if not channels:
                channels = db.get_options('DataRecorder', 'number_channels',
                                          {'brand': self.brand, 'type_recorder': 'Сетевые (IP)', 'number_poe': 0}, '=')
                recorder = db.get_data_equipments('DataRecorder',
                                                  columns,
                                                  {
                                                      'brand': self.brand,
                                                      'number_channels': channels[-1],
                                                      'type_recorder': 'Сетевые (IP)',
                                                      'number_poe': 0
                                                  })
                hdd = self.find_hdd(recorder[0], channels[-1])
                if not hdd[0]:
                    return False, hdd[-1] * recorder[0][0] * 1024 / 24 / channels[-1]
                cams -= channels[-1]
                records.append([recorder[0], hdd])
                continue

            number_channels = None
            for channel in channels:
                if cams <= channel:
                    number_channels = channel
                    break
            recorder = db.get_data_equipments('DataRecorder', columns,
                                              {'brand': self.brand, 'number_channels': number_channels, 'type_recorder': 'Сетевые (IP)'})
            hdd = self.find_hdd(recorder[0], cams)
            if not hdd[0]:
                return False, hdd[-1] * recorder[0][0] * 1024 / 24 / cams
            records.append([recorder[0], hdd])
            break

        return records

    def find_recorder(self, cams):
        records = list()
        columns = 'number_hdd, model, max_size_hdd'
        while True:
            channels = db.get_options('DataRecorder', 'number_channels',
                                      {'number_channels': cams, 'type_recorder': 'Сетевые (IP)', 'number_poe': 0},
                                      '>=')
            if not channels:
                channels = db.get_options('DataRecorder', 'number_channels',
                                          {'type_recorder': 'Сетевые (IP)', 'number_poe': 0}, '=')
                recorder = db.get_data_equipments('DataRecorder',
                                                  columns,
                                                  {
                                                      'number_channels': channels[-1],
                                                      'type_recorder': 'Сетевые (IP)',
                                                      'number_poe': 0
                                                  })
                hdd = self.find_hdd(recorder[0], channels[-1])
                if not hdd[0]:
                    return False, hdd[-1] * recorder[0][0] * 1024 / 24 / channels[-1]
                cams -= channels[-1]
                records.append([recorder[0], hdd])
                continue

            number_channels = None
            for channel in channels:
                if cams <= channel:
                    number_channels = channel
                    break
            recorder = db.get_data_equipments('DataRecorder', columns,
                                              {'number_channels': number_channels, 'type_recorder': 'Сетевые (IP)', 'number_poe': 0})
            hdd = self.find_hdd(recorder[0], cams)
            if not hdd[0]:
                return False, hdd[-1] * recorder[0][0] * 1024 / 24 / cams
            records.append([recorder[0], hdd])
            break

        return records
    # [[(2, 'DHI-NVR5232-16P-4KS2E', 10), (10.0, 2)], [(1, 'DS-N316 (B)', 6), (6.0, 1)]]
    # [[(2, 'DHI-NVR5232-16P-4KS2E', 10), (8.0, 2)]]
    # def find_recorder(self):
    #     """
    #     Заполняте список self.result словарями. Каждый словарь - отдельный регистратор. Функция добавляет ключ
    #     количества каналов для каждого регистратора.
    #     """
    #     cams = self.cams
    #     while True:
    #         recorder = self.find_recorder_channels(self.brand, cams)
    #         if recorder:
    #             break
    #         recorder = self.find_recorder_channels(self.brand)
    #         self.result.append({'number_channels': recorder[-1]})
    #         cams -= recorder[-1]
    #     self.result.append({'number_channels': recorder[0]})
    #     return self.result

    # def find_hdd_for_one_recorder(self):
    #     """
    #     Запускается если для КП нужен один регистратор. Вычисляет сколько нужно дисков для регистратора и какого
    #     размера.
    #     """
    #     max_size = db.get_options('DataRecorder',
    #                               'max_size_hdd',
    #                               {'brand': self.brand, 'number_channels': self.result[0]['number_channels']},
    #                               '=')
    #     brand_hdd = db.select_choice_equipment('brand', {'id_tg': self.id_tg}, 'ChoiceHDD')
    #     if brand_hdd:
    #         sizes_hdd = db.get_hdd_memory_size(memory_size=max_size[0], brand=brand_hdd)
    #     else:
    #         sizes_hdd = db.get_hdd_memory_size(memory_size=max_size[0])
    #     # max_number_hdd = sum(2 if i['number_channels'] != 4 else 1 for i in self.result)
    #     need_memory_size = self.cams * 24 * self.archive / 1024
    #     # print('Need_memory_size: ', need_memory_size)
    #     # print('Sizes hdd: ', sizes_hdd)
    #     for hdd in sizes_hdd:
    #         if need_memory_size < hdd:
    #             self.result[0]['number_hdd'] = 1
    #             self.result[0]['size_hdd'] = hdd
    #             return True
    #     for hdd in sizes_hdd:
    #         if need_memory_size / 2 < hdd:
    #             self.result[0]['number_hdd'] = 2
    #             self.result[0]['size_hdd'] = hdd
    #             return True
    #     return False
    #
    # def find_hdd_for_several_recorder(self):
    #     """
    #     Запускается если нужно несколько регистраторов. Вычисляет сколько нужно дисков для каждого регистратора и
    #     какого размера
    #     """
    #     cams = self.cams
    #     # sizes_hdd = db.get_hdd_memory_size()
    #     for index, recorder in enumerate(self.result):
    #         if len(self.result) - 1 == index:
    #             need_memory_size = cams * 24 * self.archive / 1024
    #         else:
    #             need_memory_size = recorder['number_channels'] * 24 * self.archive / 1024
    #         flg = False
    #         max_size = db.get_options('DataRecorder',
    #                                   'max_size_hdd',
    #                                   {'brand': self.brand, 'number_channels': recorder['number_channels']},
    #                                   '=')
    #         sizes_hdd = db.get_hdd_memory_size(memory_size=max_size[0])
    #         for hdd in sizes_hdd:
    #             if need_memory_size < hdd:
    #                 recorder['number_hdd'] = 1
    #                 recorder['size_hdd'] = hdd
    #                 flg = True
    #                 break
    #         if not flg:
    #             need_memory_size /= 2
    #             for hdd in sizes_hdd:
    #                 if need_memory_size < hdd:
    #                     recorder['number_hdd'] = 2
    #                     recorder['size_hdd'] = hdd
    #                     flg = True
    #                     break
    #         cams -= recorder['number_channels']
    #         if not flg:
    #             return False
    #     return True

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
        # print(recorder)
        # exit()
        return recorder
        # self.find_recorder()
        # if len(self.result) == 1:
        #     hdd = self.find_hdd_for_one_recorder()
        # else:
        #     hdd = self.find_hdd_for_several_recorder()
        # if not hdd:
        #     return False
        # return self.result


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
        for recorder in self.recorders:
            if recorder[0][1] in dict_rec:
                dict_rec[recorder[0][1]] += 1
            else:
                dict_rec[recorder[0][1]] = 1
        return dict_rec

    def create_row_recorder(self):
        recorders = self.create_dict_recorder()
        for model, cnt in recorders.items():
            data = self.get_data_recorder(model)[0]
            price = str(data[1]).replace(',', '.')
            row = [f"{data[2]} {data[0]} {data[-1]}",
                   "шт",
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

    # def get_data_recorder_1(self, recorder: dict):
    #     recorder = recorder.copy()
    #     recorder.pop('size_hdd')
    #     recorder['id_tg'] = self.id_tg
    #     selected_recorder = db.select_choice_equipment('model', recorder, 'ChoiceRecorder')
    #     columns = ', '.join(['model', 'price', 'description'])
    #     if not selected_recorder:
    #         recorder.pop('id_tg')
    #         recorder['brand'] = self.brand
    #         selected_recorder = db.get_data_equipments('DataRecorder', columns, recorder)
    #         if not selected_recorder:
    #             recorder['number_hdd'] += 1
    #             selected_recorder = db.get_data_equipments('DataRecorder', columns, recorder)
    #             if not selected_recorder:
    #                 recorder['number_hdd'] = 1
    #                 recorder.pop('brand')
    #                 selected_recorder = db.get_data_equipments('DataRecorder', columns, recorder)
    #                 if not selected_recorder:
    #                     recorder['number_hdd'] += 1
    #                     selected_recorder = db.get_data_equipments('DataRecorder', columns, recorder)
    #         selected_recorder = selected_recorder[0]
    #
    #     else:
    #         selected_recorder = db.get_equipment_data_by_model('DataRecorder', columns, selected_recorder)
    #
    #     # print(selected_recorder)
    #     return selected_recorder
    #
    # def create_list_recorder(self):
    #     result = list()
    #     for recorder in self.recorders:
    #         row = self.get_data_recorder(recorder)
    #         result.append(row)
    #
    #     return result
    #
    # def get_data_hdd(self, size):
    #     hdd = db.select_choice_equipment('brand', {'id_tg': self.id_tg}, 'ChoiceHDD')
    #     columns = ', '.join(('model', 'price', 'description'))
    #     if not hdd:
    #         filters = {'memory_size': size}
    #     else:
    #         filters = {'memory_size': size, 'brand': hdd}
    #     hdd = db.get_data_equipments('DataHDD', columns, filters)
    #     return hdd
    #
    # def create_list_hdd(self):
    #     result = list()
    #     for hdd in self.recorders:
    #         row = self.get_data_hdd(hdd['size_hdd'])[0]
    #         for _ in range(hdd['number_hdd']):
    #             result.append(row)
    #     return result
    #
    # def create_dict_equipments(self):
    #     result = dict()
    #     recorders = self.create_list_recorder()
    #     for recorder in recorders:
    #         if recorder in result:
    #             result[recorder] += 1
    #         else:
    #             result[recorder] = 1
    #     hdd_s = self.create_list_hdd()
    #     for hdd in hdd_s:
    #         if hdd in result:
    #             result[hdd] += 1
    #         else:
    #             result[hdd] = 1
    #     return result

    # def create_rows(self):
    #     for key, value in self.create_dict_equipments().items():
    #         price = str(key[1]).replace(',', '.')
    #         row = [f"Модель {key[0]}\n{key[-1]}",
    #                'шт',
    #                value,
    #                f"{Decimal(price).quantize(Decimal('.01'))}",
    #                f"{(Decimal(price) * value).quantize(Decimal('.01'))}"]
    #         self.result.append(row)
    #
    #     return self.result

    def main(self):
        self.create_row_recorder()
        self.create_row_hdd()
        # for i in self.result:
        #     print(*i, sep='\n')
        #     print('*' * 50)
        # # print(self.result)
        # exit()
        return self.result

# a = Recorders(cams=27, archive=11, brand='HiWatch')
# b = RowRecorderAndHDD(recorders=a.main(), brand='HiWatch', id_tg=123)
# print(*b.create_rows(), sep='\n')

# print(a.main())
# print(a.result)
