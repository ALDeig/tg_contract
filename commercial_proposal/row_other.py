from decimal import Decimal

import db


class Cable:

    def __init__(self, meters_in, meters_out, id_tg):
        self.meters_in = meters_in
        self.meters_out = meters_out
        self.id_tg = id_tg

    def get_brand(self, use):
        brand = db.select_choice_equipment('brand', {'type_system': 'IP', 'use': use}, 'ChoiceCable')
        if brand:
            return brand
        else:
            return False

    def get_data(self, use):
        brand = self.get_brand(use)
        columns = 'model, price, brand, description'
        if brand:
            data = db.get_data_equipments('DataCable', columns, {'type_system': 'IP', 'type_cable': 'Кабель', 'brand': brand, 'use': use})
        else:
            data = db.get_data_equipments('DataCable', columns, {'type_system': 'IP', 'type_cable': 'Кабель', 'use': use})
        return data[0]

    def create_row(self):
        result = []
        if self.meters_in != 0:
            data = self.get_data('Внутренний')
            price = str(data[1]).replace(',', '.')
            row = [f"{data[2]} {data[0]}, {data[-1]}",
                   'м',
                   self.meters_in,
                   f"{Decimal(price).quantize(Decimal('.01'))}",
                   f"{(Decimal(price) * Decimal(str(self.meters_in).replace(',', '.'))).quantize(Decimal('.01'))}"]
            result.append(row)
        if self.meters_out != 0:
            data = self.get_data('Внешний')
            price = str(data[1]).replace(',', '.')
            row = [f"Модель {data[0]}, {data[-1]}",
                   'м',
                   self.meters_in,
                   f"{Decimal(price).quantize(Decimal('.01'))}",
                   f"{(Decimal(price) * Decimal(str(self.meters_in).replace(',', '.'))).quantize(Decimal('.01'))}"]
            result.append(row)
        return result


class Pipe:

    def __init__(self, meters_in, meters_out, id_tg):
        self.meters_in = meters_in
        self.meters_out = meters_out
        self.id_tg = id_tg

    def get_brand(self, use):
        brand = db.select_choice_equipment('brand', {'id_tg': self.id_tg}, 'ChoiceGofra')
        if brand:
            return brand
        else:
            return False

    def get_data(self, use):
        brand = self.get_brand(use)
        columns = 'model, price, brand, description'
        if brand:
            data = db.get_data_equipments('DataCable', columns,
                                          {'type_cable': 'Гофра', 'brand': brand, 'use': use})
        else:
            data = db.get_data_equipments('DataCable', columns, {'type_cable': 'Гофра', 'use': use})
        return data[0]

    def create_row(self):
        result = []
        if self.meters_in != 0:
            data = self.get_data('Внутренняя')
            price = str(data[1]).replace(',', '.')
            row = [f"{data[2]} {data[0]}, {data[-1]}",
                   'м',
                   self.meters_in,
                   f"{Decimal(price).quantize(Decimal('.01'))}",
                   f"{(Decimal(price) * Decimal(str(self.meters_in).replace(',', '.'))).quantize(Decimal('.01'))}"]
            result.append(row)
        if self.meters_out != 0:
            data = self.get_data('Уличная')
            price = str(data[1]).replace(',', '.')
            row = [f"{data[2]} {data[0]}, {data[-1]}",
                   'м',
                   self.meters_in,
                   f"{Decimal(price).quantize(Decimal('.01'))}",
                   f"{(Decimal(price) * Decimal(str(self.meters_in).replace(',', '.'))).quantize(Decimal('.01'))}"]
            result.append(row)
        return result


class Ibp:
    def __init__(self, total_cam, id_tg):
        self.total_cam = total_cam
        self.id_tg = id_tg

    def get_brand(self, use):
        brand = db.select_choice_equipment('brand', {'id_tg': self.id_tg}, 'ChoiceIBP')
        if brand:
            return brand
        else:
            return False

    def get_data(self, power):
        brand = self.get_brand(power)
        columns = 'model, price, brand, description'
        if brand:
            data = db.get_data_equipments('DataIBP', columns, {'power': power, 'brand': brand})
        else:
            data = db.get_data_equipments('DataIBP', columns, {'power': power})
        return data

    def create_row(self):
        result = []
        if self.total_cam < 16:
            power = 850
        else:
            power = 1000
        data = self.get_data(power)[0]
        price = str(data[1]).replace(',', '.')
        row = [f"{data[2]} {data[0]}\n{data[-1]}",
               'шт',
               1,
               f"{Decimal(price).quantize(Decimal('.01'))}",
               f"{Decimal(price).quantize(Decimal('.01'))}"]
        result.append(row)
        return result


class Box:

    def __init__(self, cams_in, cams_out, model_in=None, model_out=None):
        self.cams_out = int(cams_out)
        self.cams_in = int(cams_in)
        self.model_in = model_in
        self.model_out = model_out

    @staticmethod
    def get_data(model):
        columns = 'model, price, brand, description'
        data = db.get_data_equipments('DataBracing', columns, {'model': model})
        return data[0]

    def create_row(self):
        result = list()
        if self.model_out == self.model_in:
            data = self.get_data(model=self.model_in)
            price = str(data[1]).replace(',', '.')
            row = [
                f"{data[2]} {data[0]} {data[-1]}",
                'шт',
                self.cams_out + self.cams_in,
                f"{Decimal(price).quantize(Decimal('.01'))}",
                Decimal(price).quantize(Decimal('.01')) * (self.cams_out + self.cams_in)
            ]
            result.append(row)
            return result
        if self.model_in:
            data = self.get_data(model=self.model_in)
            price = str(data[1]).replace(',', '.')
            row = [
                f"{data[2]} {data[0]}\n{data[-1]}",
                'шт',
                self.cams_in,
                f"{Decimal(price).quantize(Decimal('.01'))}",
                Decimal(price).quantize(Decimal('.01')) * self.cams_in
            ]
            result.append(row)
        if self.model_out:
            data = self.get_data(model=self.model_out)
            price = str(data[1]).replace(',', '.')
            row = [
                f"{data[2]} {data[0]}\n{data[-1]}",
                'шт',
                self.cams_out,
                f"{Decimal(price).quantize(Decimal('.01'))}",
                Decimal(price).quantize(Decimal('.01')) * self.cams_out
            ]
            result.append(row)
        return result

