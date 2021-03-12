import os

import asyncio
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, InputFile, ReplyKeyboardRemove

import analytics
import db
from keyboards import keyboards
from commercial_proposal import calculate_kp, create_doc
# from handlers.get_cost_of_work import DataPrices
from misc import dp
from utils.gmail.sendMessage import send_message


class DataPoll(StatesGroup):
    system = State()
    total_numb_of_cam = State()  # total_cams
    indoor_cameras = State()  # cams_on_indoor
    cams_on_street = State()  # cams_on_street
    type_cams_in_room = State()  # type_cam_on_street
    type_cams_on_street = State()  # type_cam_in_room
    days_for_archive = State()  # days_for_archive
    send_kp = State()
    answer_of_sale = State()


class DataPrices(StatesGroup):
    installation_cost_of_1_IP_camera = State()  # стоимость монтажа 1 IP камеры, без прокладки кабеля
    installation_cost_of_1_meter = State()  # стоимость монтажа 1 метра кабеля в гофрированной трубе
    meters_of_cable = State()  # сколько метров кабеля в среднем надо учитывать в КП на 1 IP камеру
    cost_of_mount_kit = State()  # стоимость монтажного комплекта (стяжки, коннектора, изолента, клипсы) для 1 IP камеры
    start_up_cost = State()  # стоимость пуско-наладочных работ


def generate_choice_cam(id_tg, view_cam, purpose, type_cam):
    """Создает сообщение с фото после выборы типа камеры. Какая камера будет использоваться в КП"""
    camera = db.get_model_camera_of_user(view_cam, purpose, id_tg)
    if not camera:
        details_camera = db.get_price_of_camera(type_cam=type_cam, view_cam=view_cam, purpose=purpose, ppi='2')
    else:
        details_camera = db.get_price_of_camera(camera[0])  # 'model', 'description', 'specifications', 'price', 'ppi', 'box', 'image', 'brand'
        if not details_camera:
            details_camera = db.get_price_of_camera(type_cam=type_cam, view_cam=view_cam, purpose=purpose, ppi='2')

    return details_camera


# @dp.message_handler(text='💰 Создать КП')
# async def start_poll(message: Message):
#     if db.check_user_in(id_tg=message.from_user.id, column='id_tg', table='cost_work'):  # проверяет есть ли данные в базе
#         keyboard = keyboards.create_keyboard_kp('type_cam', 'data_cameras')
#         await message.answer('Какое общее количество камер надо установить?', reply_markup=keyboards.key_cancel)
#         await DataPoll.first()
#         return
#     await message.answer('Укажите стоимость монтажа 1 IP камеры, без прокладки кабеля',
#                          reply_markup=keyboards.key_cancel)
#     await DataPrices.first()

@dp.message_handler(text='💰 Создать КП')
async def start_poll(message: Message):
    # if db.check_user_in(id_tg=message.from_user.id, column='id_tg',
    #                     table='cost_work'):  # проверяет есть ли данные в базе
    await message.answer('Выберите тип системы', reply_markup=keyboards.select_system)
    await DataPoll.first()
        # return
    # await message.answer('Укажите стоимость монтажа 1 IP камеры, без прокладки кабеля',
    #                      reply_markup=keyboards.key_cancel)
    # await DataPrices.first()


@dp.message_handler(text='IP', state=DataPoll.system)
async def step_0(message: Message, state: FSMContext):
    if db.check_user_in(id_tg=message.from_user.id, column='id_tg',
                        table='cost_work'):  # проверяет есть ли данные в базе
        await message.answer('Какое общее количество камер надо установить?',
                             reply_markup=keyboards.key_cancel_to_video)
        await DataPoll.next()
        return
    await message.answer('Укажите стоимость монтажа 1 IP камеры, без прокладки кабеля',
                         reply_markup=keyboards.key_cancel)
    await DataPrices.first()
    return
    # await state.update_data(type_cam='IP')
    await message.answer('Какое общее количество камер надо установить?', reply_markup=keyboards.key_cancel_to_video)
    await DataPoll.next()


@dp.message_handler(state=DataPoll.total_numb_of_cam)
async def step_1(message: Message, state: FSMContext):
    if not message.text.isdigit() or message.text == '0':
        await message.answer('Вы не верно указали количество. Сколько камер надо установить?',
                             reply_markup=keyboards.key_cancel_to_video)
        return
    await state.update_data(total_cams=message.text)
    await DataPoll.next()
    await message.answer('Сколько камер будет в помещении?', reply_markup=keyboards.key_cancel_to_video)


@dp.message_handler(state=DataPoll.indoor_cameras)
async def step_2(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Вы не верно указали количество. Сколько камер будут установлены в помещении?')
        return
    async with state.proxy() as data:
        total_cams = data['total_cams']
        if int(total_cams) < int(message.text):
            await message.answer('Вы неверно указали количество. Сколько камер будет установлено в помещении?')
            return
        data['cams_on_indoor'] = message.text
        data['cams_on_street'] = str(int(total_cams) - int(message.text))
    if message.text == total_cams:
        await message.answer('Все камеры будут для помещения')
        await message.answer(text='Какой тип камер будет установлен в помещении? Выбери варинат.',
                             reply_markup=keyboards.create_keyboard_kp(
                                 'view_cam',
                                 'data_cameras',
                                 {'type_cam': 'IP', 'purpose': 'Внутренние'})[0])
        await DataPoll.type_cams_in_room.set()
    elif message.text == '0':
        await message.answer('Все камеры будут уличные')
        await state.update_data(type_cam_in_room=None)
        await message.answer(text='Какой тип камер будет установлен на улице?',
                             reply_markup=keyboards.create_keyboard_kp('view_cam', 'data_cameras',
                                                                       {'type_cam': 'IP', 'purpose': 'Уличные'})[0])
        await DataPoll.type_cams_on_street.set()
    else:
        await message.answer(f'В помещении - {message.text}\nНа улице - {int(total_cams) - int(message.text)}')
        await message.answer(text='Какой тип камер будет установлен в помещении? Выбери варинат.',
                             reply_markup=keyboards.create_keyboard_kp('view_cam', 'data_cameras',
                                                                       {'type_cam': 'IP', 'purpose': 'Внутренние'})[0])
        await DataPoll.type_cams_in_room.set()


@dp.message_handler(state=DataPoll.type_cams_in_room)
async def step_4(message: Message, state: FSMContext):
    await state.update_data(type_cam_in_room=message.text)
    details_camera = generate_choice_cam(message.from_user.id, message.text[2:], 'Внутренние', 'IP')
    name = details_camera[0].strip().replace('/', '').replace('\\', '')
    # type_file = details_camera[-3].split('.')[-1]
    try:
        file = InputFile(
            os.path.join('commercial_proposal', 'images', 'camera', details_camera[-1], name + '.jpg'))
        # print('Brand camera in ', details_camera[-1])
        await message.answer_photo(photo=file, caption=f'Будет использована камера:\n'
                                                       f'{details_camera[0]}, {details_camera[1]}\n'
                                                       f'Цена: {details_camera[3]} руб.')
    except FileNotFoundError:
        await message.answer(text=f'Будет использована камера:\n'
                                  f'{details_camera[0]}, {details_camera[1]}\n'
                                  f'Цена: {details_camera[3]} руб.')
    await state.update_data(data_cam_in=details_camera)
    async with state.proxy() as data:
        if data['cams_on_indoor'] == data['total_cams']:
            data['type_cam_on_street'] = None
            await message.answer('Сколько дней хранить архив с камер видеонаблюдения?',
                                 reply_markup=keyboards.key_cancel_to_video)
            await DataPoll.days_for_archive.set()
            return
    await message.answer(text='Какой тип камер будет установлен на улице?',
                         reply_markup=keyboards.create_keyboard_kp('view_cam', 'data_cameras',
                                                                   {'type_cam': 'IP', 'purpose': 'Уличные'})[0])
    await DataPoll.next()


@dp.message_handler(state=DataPoll.type_cams_on_street)
async def step_5(message: Message, state: FSMContext):
    camera = generate_choice_cam(message.from_user.id, message.text[2:], 'Уличные', 'IP')  # 'model', 'description', 'specifications', 'price', 'ppi', 'image', 'box', 'brand'
    name = camera[0].strip().replace('/', '').replace('\\', '')
    # type_file = camera[-3].split('.')[-1]
    try:
        file = InputFile(os.path.join('commercial_proposal', 'images', 'camera', camera[-1], name + '.jpg'))
        await message.answer_photo(photo=file, caption=f'Будет использована камера:\n'
                                                       f'{camera[0]}, {camera[1]}\n'
                                                       f'Цена: {camera[3]} руб.')
    except FileNotFoundError:
        await message.answer(text=f'Будет использована камера:\n'
                                  f'{camera[0]}, {camera[1]}\n'
                                  f'Цена: {camera[3]} руб.')
    await state.update_data(type_cam_on_street=message.text)
    await state.update_data(data_cam_out=camera)
    await message.answer('Сколько дней хранить архив с камер видеонаблюдения?',
                         reply_markup=keyboards.key_cancel_to_video)
    await DataPoll.next()


@dp.message_handler(state=DataPoll.days_for_archive)
async def step_6(message: Message, state: FSMContext):
    if not message.text.isdigit() or message.text == '0':
        await message.answer('Вы не верно указали архив. Укажите число дней?',
                             reply_markup=keyboards.key_cancel_to_video)
        return
    await state.update_data(days_for_archive=message.text)
    data = await state.get_data()
    table_data = calculate_kp.calculate_result(data=data, id_tg=message.from_user.id)
    if not table_data[0]:
        await message.answer(
            f'Слишком большой архив для данной конфигурации. Максимальный архив {int(table_data[1])} дн.',
            reply_markup=keyboards.key_cancel_to_video)
        return
    file_name, number_kp = create_doc.save_kp(table_data[0], table_data[1]['total'], message.from_user.id)

    # await state.finish()
    await message.answer(text=f'💰<b>Общая стоимость - {table_data[1]["total"]:.2f}₽</b>\n\n'
                              f'1️⃣Стоимость оборудования - {table_data[1]["equipment"]:.2f}₽\n'
                              f'2️⃣Стоимость материалов - {table_data[1]["materials"]:.2f}₽\n'
                              f'3️⃣Стоимость работы - {table_data[1]["work"]:.2f}₽',
                         parse_mode='HTML',
                         reply_markup=ReplyKeyboardRemove())
    await message.answer('Подождите, я начал формировать КП')
    await asyncio.sleep(10)
    file = InputFile(file_name)
    await message.answer_document(file)
    old_tpl = db.get_kp_tpl(message.from_user.id)
    if not old_tpl:
        await message.answer(text='Загрузите свой шаблон КП:  https://clck.ru/S8SjN.', disable_web_page_preview=True)
    # await message.answer(text='КП готов, что дальше?', reply_markup=keyboards.menu)
    await message.answer(text='КП готов. Отправьте поставщику, чтобы получить предложение.\nОтправить?',
                         reply_markup=keyboards.yes_or_no)
    await state.update_data({'file': file_name, 'to_provider': table_data[-1]})
    await DataPoll.send_kp.set()
    analytics.insert_data('kp')
    db.write_number_kp(message.from_user.id, number_kp=int(number_kp) + 1)
    # await state.finish()
    # return
    # send_message('You won 1 mln $', file_name, 'alkin.denis@gmail.com', 'Test email')
    await asyncio.sleep(5)
    os.remove(file_name)


@dp.message_handler(state=DataPoll.send_kp)
async def send_kp_to_provider(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == 'Да':
        city = db.get_data('name, phone, city', 'users', {'id_tg': ('=', message.from_user.id)})
        text = f'Пользователь: {message.from_user.full_name}, ID: {message.from_user.id}\n' \
               f'Имя в базе: {city[0].name}\n' \
               f'Телефон: {city[0].phone}\n' \
               f'Город: {city[0].city}\n\n' \
               f'Здравствуйте.Внимание! Отправьте ответ в течении 30 мин.' \
               f'Подтвердите наличие и укажите стоимость запрашиваемого оборудования в файле.\n' \
               f'С уважением,\nКоманда Rommo'
        file_name = create_doc.save_table_to_provider(data['to_provider'], message.from_user.id)
        send_message(text, file_name, 'alkin.denis@gmail.com', 'Новый заказ от RommoBot')
        os.remove(file_name)
    await state.finish()
    await message.answer('Готово!', reply_markup=keyboards.menu)
    await asyncio.sleep(5)
