import os

import asyncio
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, InputFile, ReplyKeyboardRemove

import analytics
import db
from keyboards import keyboards
from commercial_proposal import calculate_kp, create_doc
from handlers.get_cost_of_work import DataPrices
from misc import dp


class DataPoll(StatesGroup):
    total_numb_of_cam = State()  # total_cams
    indoor_cameras = State()  # cams_on_indoor
    cams_on_street = State()  # cams_on_street
    type_cams_in_room = State()  # type_cam_on_street
    type_cams_on_street = State()  # type_cam_in_room
    days_for_archive = State()  # days_for_archive
    answer_total_price = State()
    answer_of_sale = State()


def generate_choice_cam(id_tg, type_cam, purpose):
    """Создает сообщение с фото после выборы типа камеры. Какая камера будет использоваться в КП"""
    camera = db.get_model_camera_of_user(type_cam, purpose, id_tg)
    if not camera:
        details_camera = db.get_price_of_camera(view_cam=type_cam, purpose=purpose, ppi='2')
    else:
        details_camera = db.get_price_of_camera(camera[0])

    return details_camera


@dp.message_handler(text='💰 Создать КП')
async def start_poll(message: Message):
    if db.check_user_in(id_tg=message.from_user.id, column='id_tg', table='cost_work'):  # проверяет есть ли данные в базе
        await message.answer('Какое общее количество камер надо установить?', reply_markup=keyboards.key_cancel)
        await DataPoll.first()
        return
    await message.answer('Укажите стоимость монтажа 1 IP камеры, без прокладки кабеля',
                         reply_markup=keyboards.key_cancel)
    await DataPrices.first()


@dp.message_handler(state=DataPoll.total_numb_of_cam)
async def step_1(message: Message, state: FSMContext):
    if not message.text.isdigit() or message.text == '0':
        await message.answer('Вы не верно указали количество. Сколько камер надо установить?',
                             reply_markup=keyboards.key_cancel)
        return
    await state.update_data(total_cams=message.text)
    await DataPoll.next()
    await message.answer('Сколько камер будет в помещении?', reply_markup=keyboards.key_cancel)


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
                             reply_markup=keyboards.create_keyboard_kp('view_cam', {'purpose': 'Внутренняя'})[0])
        await DataPoll.type_cams_in_room.set()
    elif message.text == '0':
        await message.answer('Все камеры будут уличные')
        await state.update_data(type_cam_in_room=None)
        await message.answer(text='Какой тип камер будет установлен на улице?',
                             reply_markup=keyboards.create_keyboard_kp('view_cam', {'purpose': 'Уличная'})[0])
        await DataPoll.type_cams_on_street.set()
    else:
        await message.answer(f'В помещении - {message.text}, значит на улице будет {int(total_cams) - int(message.text)}')
        await message.answer(text='Какой тип камер будет установлен в помещении? Выбери варинат.',
                             reply_markup=keyboards.create_keyboard_kp('view_cam', {'purpose': 'Внутренняя'})[0])
        await DataPoll.type_cams_in_room.set()


@dp.message_handler(state=DataPoll.type_cams_in_room)
async def step_4(message: Message, state: FSMContext):
    await state.update_data(type_cam_in_room=message.text)
    details_camera = generate_choice_cam(message.from_user.id, message.text[2:], 'Внутренняя')
    file = InputFile(os.path.join('commercial_proposal', 'images', details_camera[-1], details_camera[0] + '.jpg'))
    await message.answer_photo(photo=file, caption=f'Будет использована камера:\n'
                                                   f'{details_camera[0]}, {details_camera[1]}\n'
                                                   f'Цена: {details_camera[3]}')
    async with state.proxy() as data:
        if data['cams_on_indoor'] == data['total_cams']:
            data['type_cam_on_street'] = None
            await message.answer('Сколько дней хранить архив с камер видеонаблюдения?',
                                 reply_markup=keyboards.key_cancel)
            await DataPoll.days_for_archive.set()
            return
    await message.answer(text='Какой тип камер будет установлен на улице?',
                         reply_markup=keyboards.create_keyboard_kp('view_cam', {'purpose': 'Уличная'})[0])
    await DataPoll.next()


@dp.message_handler(state=DataPoll.type_cams_on_street)
async def step_5(message: Message, state: FSMContext):
    camera = generate_choice_cam(message.from_user.id, message.text[2:], 'Уличная')
    file = InputFile(os.path.join('commercial_proposal', 'images', camera[-1], camera[0] + '.jpg'))
    await message.answer_photo(photo=file, caption=f'Будет использована камера:\n'
                                                   f'{camera[0]}, {camera[1]}\n'
                                                   f'Цена: {camera[3]}')
    await state.update_data(type_cam_on_street=message.text)
    await message.answer('Сколько дней хранить архив с камер видеонаблюдения?', reply_markup=keyboards.key_cancel)
    await DataPoll.next()


@dp.message_handler(state=DataPoll.days_for_archive)
async def step_6(message: Message, state: FSMContext):
    if not message.text.isdigit() or message.text == '0':
        await message.answer('Вы не верно указали архив. Укажите число дней?', reply_markup=keyboards.key_cancel)
        return
    await state.update_data(days_for_archive=message.text)
    data = await state.get_data()
    if int(data['total_cams']) >= 16 and int(message.text) > 18:
        await message.answer(f'Слишком большой архив для данной конфигурации. Максимально возможный архив '
                             f'18 дн. Укажите сколько дней будем хранить архив.', reply_markup=keyboards.key_cancel)
        return
    table_data = calculate_kp.calculate_result(data=data, id_tg=message.from_user.id)
    if not table_data[0]:
        await message.answer(f'Слишком большой архив для данной конфигурации. Максимально возможный архив '
                             f'{table_data[1]} дн. Укажите сколько дней будем хранить архив.',
                             reply_markup=keyboards.key_cancel)
        return
    file_name, number_kp = create_doc.save_kp(table_data[0], table_data[1]['total'], message.from_user.id)

    await state.finish()
    await message.answer(text=f'Общая стоимость - {table_data[1]["total"]:.2f}₽\n'
                              f'Стоимость оборудования - {table_data[1]["equipment"]:.2f}₽\n'
                              f'Стоимость материалов - {table_data[1]["materials"]:.2f}₽\n'
                              f'Стоимость работы - {table_data[1]["work"]:.2f}₽', reply_markup=ReplyKeyboardRemove())
    await message.answer('Подождите, я начал формировать КП')
    await asyncio.sleep(10)
    file = InputFile(file_name)
    await message.answer_document(file)
    await message.answer(text='КП готов, что дальше?', reply_markup=keyboards.menu)
    analytics.insert_data('kp')
    db.write_number_kp(message.from_user.id, number_kp=int(number_kp) + 1)
    await asyncio.sleep(5)
    os.remove(file_name)
