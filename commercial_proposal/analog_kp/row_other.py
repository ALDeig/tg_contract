from decimal import Decimal

import db


class Cable:

    def __init__(self, meters_in, meters_out, id_tg):
        self.meters_in = meters_in
        self.meters_out = meters_out
        self.id_tg = id_tg

    @staticmethod
    def get_brand(use):
        brand = db.get_data('brand', 'ChoiceCable', {'type_system': ('!=', 'IP'), 'use': ('=', use)})
        if brand:
            return brand[0]
        else:
            return False

    def get_data(self, use):
        brand = self.get_brand(use)
        columns = 'model, price, brand, description'
        if brand:
            data = db.get_data(columns,
                               'DataCable',
                               {'type_system': ['!=', 'IP'],
                                'type_cable': ['=', 'Кабель'],
                                'brand': ['=', brand],
                                'use': ['=', use]})
        else:
            data = db.get_data(columns,
                               'DataCable',
                               {'type_system': ('!=', 'IP'),
                                'type_cable': ('=', 'Кабель'),
                                'use': ('=', use)})
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
                   self.meters_out,
                   f"{Decimal(price).quantize(Decimal('.01'))}",
                   f"{(Decimal(price) * Decimal(str(self.meters_out).replace(',', '.'))).quantize(Decimal('.01'))}"]
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
                   self.meters_out,
                   f"{Decimal(price).quantize(Decimal('.01'))}",
                   f"{(Decimal(price) * Decimal(str(self.meters_out).replace(',', '.'))).quantize(Decimal('.01'))}"]
            result.append(row)
        return result


class Ibp:
    def __init__(self, total_cam, id_tg):
        self.total_cam = total_cam
        self.id_tg = id_tg

    def get_brand(self, use):
        brand = db.select_choice_equipment('brand', {'id_tg': self.id_tg, 'type_ibp': 'TVI'}, 'ChoiceIBP')
        if brand:
            return brand
        else:
            return False

    def get_data(self, power):
        result = list()
        for item in power:
            brand = self.get_brand(item)
            columns = 'model, price, brand, description'
            if brand:
                data = db.get_data_equipments('DataIBP', columns, {'power': item, 'brand': brand, 'type_ibp': 'TVI'})
            else:
                data = db.get_data_equipments('DataIBP', columns, {'power': item, 'type_ibp': 'TVI'})
            result.append(data[0])
        return result

    def find_ibp(self, brand=None):
        filters = {'type_ibp': ('=', 'TVI'), 'brand': ('=', brand)} if brand else {'type_ibp': ('=', 'TVI')}
        options = db.get_types('power', 'DataIBP', filters)
        result = list()
        flg = False
        while True:
            for item in options:
                if self.total_cam < item:
                    result.append(item)
                    flg = True
                    break
            if flg:
                break
            result.append(options[-1])
            self.total_cam -= options[-1]
        return result

    def create_row(self):
        power = self.find_ibp()
        result = []
        ibps = self.get_data(power)
        for data in ibps:
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
        data = db.get_data(columns, 'DataBracing', {'model': ('=', model)})
        return data[0]

    def create_row(self):
        result = list()
        if self.model_out == self.model_in:
            data = self.get_data(model=self.model_in)
            price = str(data.price).replace(',', '.')
            row = [
                f"{data.brand} {data.model} {data.description}",
                'шт',
                self.cams_out + self.cams_in,
                f"{Decimal(price).quantize(Decimal('.01'))}",
                Decimal(price).quantize(Decimal('.01')) * (self.cams_out + self.cams_in)
            ]
            result.append(row)
            return result
        if self.model_in:
            data = self.get_data(model=self.model_in)
            price = str(data.price).replace(',', '.')
            row = [
                f"{data.brand} {data.model} {data.description}",
                'шт',
                self.cams_in,
                f"{Decimal(price).quantize(Decimal('.01'))}",
                Decimal(price).quantize(Decimal('.01')) * self.cams_in
            ]
            result.append(row)
        if self.model_out:
            data = self.get_data(model=self.model_out)
            price = str(data.price).replace(',', '.')
            row = [
                f"{data.brand} {data.model} {data.description}",
                'шт',
                self.cams_out,
                f"{Decimal(price).quantize(Decimal('.01'))}",
                Decimal(price).quantize(Decimal('.01')) * self.cams_out
            ]
            result.append(row)
        return result
