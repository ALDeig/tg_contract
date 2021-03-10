from decimal import Decimal

from loguru import logger

import db


class Locker:

    def __init__(self, recorders, switches, type_box, id_tg):
        self.units = recorders + recorders * 2
        self.type_box = type_box
        self.id_tg = id_tg
        self.result = list()

    def calculate_box_type_1(self):
        while True:
            options_units = db.get_types('number_units', 'DataBox', {'type_box': ('=', 1)})
            flg = False
            for units in options_units:
                if self.units < units:
                    self.result.append(units)
                    flg = True
                    break
            if flg:
                return self.result
            else:
                self.result.append(options_units[-1])
                self.units -= options_units[-1]
                # return self.result

    def calculate_box_type_0(self):
        choice_box = db.get_data('model', 'ChoiceBox', {'type_box': ('=', 0), 'id_tg': ('=', self.id_tg)})
        columns = 'model, price, brand, description'
        if not choice_box:
            box = db.get_data(columns, 'DataBox', {'type_box': ('=', 0)})
        else:
            box = db.get_data(columns, 'DataBox', {'model': ('=', choice_box[0].model)})
        return {box[0]: 1}

    def get_data_box(self, units):
        select_box = db.get_data('model', 'ChoiceBox', {'number_units': ('=', units),
                                                        'id_tg': ('=', self.id_tg),
                                                        'type_box': ('=', 1)})
        columns = ', '.join(('model', 'price', 'brand', 'description'))
        if not select_box:
            box = db.get_data(columns, 'DataBox', {'number_units': ('=', units), 'type_box': ('=', 1)})
        else:
            box = db.get_data(columns, 'DataBox', {'model': ('=', select_box)})
            if not box:
                box = db.get_data(columns, 'DataBox', {'number_units': ('=', units), 'type_box': ('=', 1)})
        print(box[0])
        return box[0]

    def create_dict_boxes(self, boxes):
        result = {}
        for box in boxes:
            data = self.get_data_box(box)
            if data in result:
                result[data] += 1
            else:
                result[data] = 1

        return result

    @staticmethod
    def create_rows(boxes):
        result = list()
        for data, count in boxes.items():
            price = str(data[1]).replace(',', '.')
            row = [f"{data[2]} {data[0]} {data[-1]}",
                   'шт',
                   count,
                   f"{Decimal(price).quantize(Decimal('.01'))}",
                   f"{(Decimal(price) * count).quantize(Decimal('.01'))}"]
            result.append(row)

        return result

    @staticmethod
    def create_row_dsk():
        columns = 'model, price, brand, description'
        data = db.get_data(columns=columns, table='DataBox', filters={'type_box': ('=', 2)})[0]
        price = str(data.price).replace(',', '.')
        row = [f"{data.brand} {data.model} {data.description}",
               'шт',
               1,
               f"{Decimal(price).quantize(Decimal('.01'))}",
               f"{(Decimal(price) * 1).quantize(Decimal('.01'))}"]
        return row

    def main(self):
        if self.type_box == 0:
            box = self.calculate_box_type_0()
        else:
            units = self.calculate_box_type_1()
            box = self.create_dict_boxes(units)
        row = self.create_rows(box)
        if self.type_box == 0:
            row.append(self.create_row_dsk())
        logger.debug(row)
        return row
