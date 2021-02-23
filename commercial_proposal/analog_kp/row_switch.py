from decimal import Decimal

import db


class Switch:
    """Класс в котором формируется словарь с коммутаторами"""

    def __init__(self, cams, brand):
        self.cams = cams
        self.brand = brand
        self.result = list()

    def check_brand(self):
        brand = db.get_options('DataSwitch', 'brand')
        if self.brand in brand:
            return True
        else:
            return False

    def get_options_ports(self):
        brand = self.check_brand()
        if brand:
            options_ports = db.get_options('DataSwitch', 'number_ports', {'brand': self.brand}, '=')
        else:
            options_ports = db.get_options('DataSwitch', 'number_ports')
        return options_ports

    def calculate_switch(self):
        while True:
            options_ports = self.get_options_ports()
            if not options_ports:
                return False
            flg = False
            for port in options_ports:
                if self.cams < port:
                    self.result.append(port)
                    flg = True
                    break
            if flg:
                return self.result
            else:
                self.cams -= options_ports[-1]
                self.result.append(options_ports[-1])


class RowsSwitch:
    """Класс создает строки с коммутаторами"""

    def __init__(self, switches, id_tg, brand):
        self.switches = switches
        self.id_tg = id_tg
        self.brand = brand
        self.result = list()

    def check_brand(self):
        brand = db.get_options('DataSwitch', 'brand')
        if self.brand in brand:
            return True
        else:
            return False

    def get_data_switch(self, ports):
        brand = self.check_brand()
        select_switch = db.select_choice_equipment('model', {'ports_poe': ports, 'id_tg': self.id_tg}, 'ChoiceSwitch')
        columns = ', '.join(('model', 'price', 'brand', 'description'))
        if not select_switch:
            if brand:
                switch = db.get_data_equipments('DataSwitch', columns, {'ports_poe': ports, 'brand': self.brand})[0]
            else:
                switch = db.get_data_equipments('DataSwitch', columns, {'ports_poe': ports})[0]
        else:
            switch = db.get_equipment_data_by_model('DataSwitch', columns, select_switch)

        return switch

    def create_dict_switches(self):
        result = {}
        for switch in self.switches:
            data = self.get_data_switch(switch)
            if data in result:
                result[data] += 1
            else:
                result[data] = 1

        return result

    def create_rows(self):
        switches = self.create_dict_switches()
        for data, count in switches.items():
            price = str(data[1]).replace(',', '.')
            row = [f"{data[2]} {data[0]} {data[-1]}",
                   'шт',
                   count,
                   f"{Decimal(price).quantize(Decimal('.01'))}",
                   f"{(Decimal(price) * count).quantize(Decimal('.01'))}"]
            self.result.append(row)

        return self.result








# a = Switch(5, 'HiWatch')
# print(a.calculate_switch())




