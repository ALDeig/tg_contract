from decimal import Decimal

import db


class Locker:

    def __init__(self, recorders, switches):
        self.units = recorders + recorders * 2
        self.result = list()

    @staticmethod
    def get_options_units():
        options_units = db.get_options('DataBox', 'number_units')
        return options_units

    def calculate_box(self):
        while True:
            options_units = self.get_options_units()
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
                return self.result


class RowBox:

    def __init__(self, id_tg, boxes):
        self.boxes = boxes
        print('Boxes: ', self.boxes)
        self.id_tg = id_tg
        self.result = list()

    def get_data_box(self, units):
        select_box = db.select_choice_equipment('model', {'number_units': units, 'id_tg': self.id_tg}, 'ChoiceBox')
        print('Select box: ', select_box)
        columns = ', '.join(('model', 'price', 'brand', 'description'))
        if not select_box:
            box = db.get_data_equipments('DataBox', columns, {'number_units': units})[0]
        else:
            box = db.get_data_equipments('DataBox', columns, {'model': select_box})[0]
            if not box:
                box = db.get_data_equipments('DataBox', columns, {'number_units': units})[0]
        return box

    def create_dict_boxes(self):
        result = {}
        for box in self.boxes:
            data = self.get_data_box(box)
            if data in result:
                result[data] += 1
            else:
                result[data] = 1

        return result

    def create_rows(self):
        switches = self.create_dict_boxes()
        for data, count in switches.items():
            price = str(data[1]).replace(',', '.')
            row = [f"{data[2]} {data[0]} {data[-1]}",
                   'шт',
                   count,
                   f"{Decimal(price).quantize(Decimal('.01'))}",
                   f"{(Decimal(price) * count).quantize(Decimal('.01'))}"]
            self.result.append(row)

        return self.result
