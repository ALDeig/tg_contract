import requests
import os
import shutil
from pathlib import Path
from decimal import Decimal
from typing import NamedTuple

from google_drive_downloader import GoogleDriveDownloader as gdd
from loguru import logger

import db


class CostWork(NamedTuple):
    name: str
    price: str


class SignalingKp:
    def __init__(self, data, id_tg):
        self.data = data
        self.id_tg = str(id_tg)
        self.choice_protection = data.pop('choice_protection')
        self.add_devices = data.pop('add_devices') if 'add_devices' in data else None
        self.cost_work = self.get_cost_work()
        self.result = dict()
        self.work = dict()
        self.total_cost_work = 0
        self.total_cost_equipments = 0
        self.columns = 'name, price'
        hub = self.add_hub()
        self.result['row_1'] = ['Оборудование']
        self.result['hub'] = self.create_row(hub[0], hub[1], 'equipment')

    def add_hub(self):
        hub = self.get_data_of_device(table='hub', name='Hub')
        rooms = int(self.data['rooms'])
        number_hub = rooms // 50 if rooms % 50 == 0 else rooms // 50 + 1
        return hub, number_hub

    def get_cost_work(self):
        columns = 'motion_sensor, open_sensor, smoke_detector, leakage_sensor, siren, control_keyboard, ' \
                  'smart_plug, power_relay, low_current_relay'
        cost = db.get_data(columns, 'cost_signaling', {'id_tg': ('=', self.id_tg)})
        if cost:
            return cost[0]

    def get_data_of_device(self, table: str, name: str = None):
        select_tables = {'hub': 'SelectHub', 'invasion': 'SelectInvasion', 'siren': 'SelectSiren',
                         'control': 'SelectControl', 'bbp': 'SelectBBP', 'fire': 'SelectFire',
                         'leak': 'SelectLeak'}
        select_device = db.get_data('name', select_tables[table])
        if select_device:
            data = db.get_data(self.columns, table, {'name': ('=', select_device[0].name)})[0]
        else:
            data = db.get_data(self.columns, table, {'name': ('=', name)})[0]
        return data

    def create_row(self, data, number, category):
        price = float(data.price) * number
        if category == 'work':
            self.total_cost_work += price
        else:
            self.total_cost_equipments += price
        result = [
            f'{data.name}',
            'шт',
            number,
            Decimal(str(data.price)).quantize(Decimal('.01')),
            Decimal(str(price)).quantize(Decimal('.01'))
        ]
        return result

    def intrusion_protection(self):
        open_door = self.get_data_of_device('invasion', 'DoorProtect')
        motion_protect = self.get_data_of_device('invasion', 'MotionProtect')
        siren = self.get_data_of_device('siren', 'HomeSiren')
        space_control = self.get_data_of_device('control', 'SpaceControl')
        self.result['open_door'] = self.create_row(open_door, 1, 'equipment')
        self.work['open_work'] = self.create_row(
            CostWork(name='Монтаж датчиков открытия', price=self.cost_work.open_sensor),
            1 if self.data['floor'] == 'Другой' else int(self.data['rooms']) + 1,
            'work'
        )
        self.result['motion_protect'] = self.create_row(motion_protect, int(self.data['rooms']), 'equipment')
        self.work['motion_protect_work'] = self.create_row(
            CostWork(name='Монтаж датчиков движения', price=self.cost_work.motion_sensor),
            int(self.data['rooms']),
            'work'
        )
        self.result['siren'] = self.create_row(siren, 1, 'equipment')
        self.work['siren_work'] = self.create_row(
            CostWork(name='Установка сирены', price=self.cost_work.siren),
            1,
            'work'
        )
        self.result['space_control'] = self.create_row(space_control, 1, 'equipment')
        if self.data['floor'] != 'Другой':
            open_window = db.get_data(self.columns, 'invasion', {'name': ('=', 'CombiProtect')})[0]
            self.result['open_window'] = self.create_row(open_window, int(self.data['rooms']), 'equipment')

    def fire_safety(self):
        fire_protect = self.get_data_of_device('fire', 'FireProtect')
        self.result['fire_protect'] = self.create_row(fire_protect, int(self.data['rooms']), 'equipment')
        self.work['fire_protect_work'] = self.create_row(
            CostWork(name='Монтаж датчиков дыма', price=self.cost_work.smoke_detector),
            int(self.data['rooms']),
            'work'
        )

    def leakage_protection(self):
        leak = self.get_data_of_device('leak', 'LeaksProtect')
        self.result['leak'] = self.create_row(leak, int(self.data['bedrooms']), 'equipment')
        self.work['leak_work'] = self.create_row(
            CostWork(name='Монтаж датчиков протечки', price=self.cost_work.leakage_sensor),
            int(self.data['bedrooms']),
            'work'
        )

    def street_guard(self):
        motion_protect_outdoor = db.get_data(self.columns, 'invasion', {'name': ('=', 'MotionProtect Outdoor')})[0]
        self.result['motion_protect_outdoor'] = self.create_row(motion_protect_outdoor, 1, 'equipment')
        if 'motion_protect_work' in self.work:
            numbers = self.work['motion_protect_work'][2] + 1
        else:
            numbers = 1
        self.work['motion_protect_work'] = self.create_row(
            CostWork(name='Монтаж датчиков движения', price=self.cost_work.motion_sensor),
            numbers,
            'work'
        )

    def add_devices_in_result(self):
        tables = {
            'fire': (self.cost_work.smoke_detector, 'Монтаж датчиков дыма'),
            'leak': (self.cost_work.leakage_sensor, 'Установка датчика протечки'),
            'siren': (self.cost_work.siren, 'Установка сирены'),
            'control': (self.cost_work.control_keyboard, 'Установка панели контроля')}
        for key, value in self.add_devices.items():
            columns = 'name, type_sensor, price' if key == 'invasion' else self.columns
            data = db.get_data(columns, key, {'name': ('=', value[0])})[0]
            self.result[f'add_{key}'] = self.create_row(data, value[1], 'equipment')
            if key == 'invasion':
                if data.type_sensor == 'm':
                    self.work['add_motion_protec_work'] = self.create_row(
                        CostWork(name='Монтаж датчиков движения', price=self.cost_work.motion_sensor),
                        value[1],
                        'work'
                    )
                else:
                    self.work['add_open_work'] = self.create_row(
                        CostWork(name='Монтаж датчиков открытия', price=self.cost_work.open_sensor),
                        value[1],
                        'work'
                    )
            else:
                if key in tables:
                    self.work['add_devices'] = self.create_row(
                        CostWork(name=tables[key][1], price=tables[key][0]),
                        value[1],
                        'work'
                    )

    def main(self):
        if self.choice_protection['intrusion_protection'] == 1:
            self.intrusion_protection()
        if self.choice_protection['fire_safety']:
            self.fire_safety()
        if self.choice_protection['leakage_protection']:
            self.leakage_protection()
        if self.choice_protection['street_guard']:
            self.street_guard()
        if self.add_devices:
            self.add_devices_in_result()
        self.result['row_2'] = ['Работа']
        self.result.update(self.work)
        return self.result, self.total_cost_work, self.total_cost_equipments


folders = ('siren', 'automation', 'bbp', 'control', 'fire', 'hub', 'integration', 'invasion', 'leak')
# device = db.get_data('name, photo', folder)
work_path = Path.cwd() / '123' / '13'
print(work_path)


def delete_dirs(directory):
    path = Path.cwd().parent.parent / 'commercial_proposal' / 'images' / 'signaling' / directory
    for index, dir_ in enumerate(os.walk(path)):
        if index == 0:
            pass
        else:
            shutil.rmtree(dir_[0])


def save_images(data, directory):
    path = Path.cwd().parent.parent / 'commercial_proposal' / 'images' / 'signaling' / directory
    # path = Path(Path.cwd().parent.parent, 'commercial_proposal', 'images', 'signaling', directory)
    # path = os.path.join(work_path, 'commercial_proposal', 'images', 'signaling', directory)
    # path = os.path.join('images', directory)
    delete_dirs(directory)
    for camera in data:
        try:
            url = camera.photo.split('/')
            if not os.path.exists(os.path.join(path, 'Ajax'.strip())):
                os.mkdir(os.path.join(path, 'Ajax'.strip()))
            if url[2] == 'drive.google.com':
                logger.info('drive.google')
                name = camera.name.strip().replace('/', '').replace('\\', '').replace(' ', '')
                path_file = os.path.join(path, 'Ajax'.strip(), name + f'.jpg')
                gdd.download_file_from_google_drive(file_id=url[-2], dest_path=path_file)
                continue
            else:
                img = requests.get(camera.photo)
        except Exception as er:
            logger.error(er)
            logger.error(camera.photo)
            continue
        if not os.path.exists(os.path.join(path, 'Ajax'.strip())):
            os.mkdir(os.path.join(path, 'Ajax'.strip()))
        name = camera.name.strip().replace('/', '').replace('\\', '').replace(' ', '')
        # type_file = camera[image_index].split('.')[-1]
        with open(os.path.join(path, 'Ajax'.strip(), name + '.jpg'), 'wb') as file:
            file.write(img.content)


def main():
    for folder in folders:
        device = db.get_data('name, photo', folder)
        save_images(device, folder)


if __name__ == '__main__':
    main()


