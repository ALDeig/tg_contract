from aiogram.dispatcher.filters.state import State, StatesGroup


class PricesAnalogKp(StatesGroup):
    installation_cost_of_1_IP_camera = State()  # стоимость монтажа 1 IP камеры, без прокладки кабеля
    installation_cost_of_1_meter = State()  # стоимость монтажа 1 метра кабеля в гофрированной трубе
    meters_of_cable = State()  # сколько метров кабеля в среднем надо учитывать в КП на 1 IP камеру
    cost_of_mount_kit = State()  # стоимость монтажного комплекта (стяжки, коннектора, изолента, клипсы) для 1 IP камеры
    start_up_cost = State()  # стоимость пуско-наладочных работ


class DataPollAnalog(StatesGroup):
    total_cams = State()  # total_cams
    cams_indoor = State()  # cams_on_indoor
    cams_on_street = State()  # cams_on_street
    type_cams_in_room = State()  # type_cam_on_street
    type_cams_on_street = State()  # type_cam_in_room
    days_for_archive = State()  # days_for_archive