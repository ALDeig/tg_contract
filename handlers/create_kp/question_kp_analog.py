import asyncio
import os

import os

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InputFile, ReplyKeyboardRemove

import analytics
import db
from keyboards.create_kp.analog_kp_keyboard import create_keyboard_kp
from keyboards import keyboards
from commercial_proposal.analog_kp import calculate_analog_kp
from commercial_proposal import create_doc
from handlers.questions_of_kp import DataPoll
from misc import dp
from states.analog_kp import PricesAnalogKp, DataPollAnalog


def generate_choice_cam(filters):
    model = db.get_data('model', 'choice_cams', filters)
    columns = 'model, description, specifications, price, ppi, image, box, brand'
    if not model:
        filters.pop('id_tg')
        camera = db.get_data(columns, 'data_cameras', filters)
    else:
        camera = db.get_data(columns, 'data_cameras', {'model': ['=', model[0].model]})
    return camera[0]


@dp.message_handler(text='Аналоговая', state=DataPoll.system)
async def step_0(message: Message, state: FSMContext):
    if db.check_user_in(id_tg=message.from_user.id, column='id_tg', table='cost_work_analog') or \
            db.check_user_in(id_tg=message.from_user.id, column='id_tg', table='cost_work'):
        await message.answer('Какое общее количество камер надо установить?', reply_markup=keyboards.key_cancel)
        await DataPollAnalog.first()
        return
    await message.answer('Укажите стоимость монтажа 1 камеры, без прокладки кабеля',
                         reply_markup=keyboards.key_cancel_to_video)
    await PricesAnalogKp.first()


@dp.message_handler(state=DataPollAnalog.total_cams)
async def step_1(msg: Message, state: FSMContext):
    if not msg.text.isdigit() or msg.text == '0':
        await msg.answer('Вы не верно указали количество. Сколько камер надо установить?',
                         reply_markup=keyboards.key_cancel_to_video)
        return
    await state.update_data(total_cams=msg.text)
    await DataPollAnalog.next()
    await msg.answer('Сколько камер будет в помещении?', reply_markup=keyboards.key_cancel_to_video)


@dp.message_handler(state=DataPollAnalog.cams_indoor)
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
                             reply_markup=create_keyboard_kp(
                                 'view_cam',
                                 'data_cameras',
                                 {'type_cam': ['!=', 'IP'], 'purpose': ['=', 'Внутренние']})[0])
        await DataPollAnalog.type_cams_in_room.set()
    elif message.text == '0':
        await message.answer('Все камеры будут уличные')
        await state.update_data(type_cam_in_room=None)
        await message.answer(text='Какой тип камер будет установлен на улице?',
                             reply_markup=create_keyboard_kp('view_cam', 'data_cameras',
                                                             {'type_cam': ['!=', 'IP'], 'purpose': ['=', 'Уличные']})[
                                 0])
        await DataPollAnalog.type_cams_on_street.set()
    else:
        await message.answer(f'В помещении - {message.text}\nНа улице - {int(total_cams) - int(message.text)}')
        await message.answer(text='Какой тип камер будет установлен в помещении? Выбери варинат.',
                             reply_markup=create_keyboard_kp('view_cam', 'data_cameras',
                                                             {'type_cam': ['!=', 'IP'],
                                                              'purpose': ['=', 'Внутренние']})[0])
        await DataPollAnalog.type_cams_in_room.set()


@dp.message_handler(state=DataPollAnalog.type_cams_in_room)
async def step_3(message: Message, state: FSMContext):
    await state.update_data(type_cam_in_room=message.text)
    camera = generate_choice_cam({
        'id_tg': ['=', message.from_user.id],
        'view_cam': ['=', message.text[2:]],
        'purpose': ['=', 'Внутренние'],
        'type_cam': ['!=', 'IP']
    })
    name = camera.model.strip().replace('/', '').replace('\\', '')
    try:
        file = InputFile(
            os.path.join('commercial_proposal', 'images', 'camera', camera.brand, name + '.jpg'))
        await message.answer_photo(photo=file, caption=f'Будет использована камера:\n'
                                                       f'{camera.model}, {camera.description}\n'
                                                       f'Цена: {camera.price} руб.')
    except FileNotFoundError:
        await message.answer(text=f'Будет использована камера:\n'
                                  f'{camera.model}, {camera.description}\n'
                                  f'Цена: {camera.price} руб.')
    await state.update_data(data_cam_in=camera)
    async with state.proxy() as data:
        if data['cams_on_indoor'] == data['total_cams']:
            data['type_cam_on_street'] = None
            await message.answer('Сколько дней хранить архив с камер видеонаблюдения?',
                                 reply_markup=keyboards.key_cancel_to_video)
            await DataPollAnalog.days_for_archive.set()
            return
    await message.answer(text='Какой тип камер будет установлен на улице?',
                         reply_markup=create_keyboard_kp('view_cam', 'data_cameras',
                                                         {'type_cam': ['!=', 'IP'],
                                                          'purpose': ['=', 'Уличные']})[0])
    await DataPollAnalog.next()


@dp.message_handler(state=DataPollAnalog.type_cams_on_street)
async def step_4(message: Message, state: FSMContext):
    camera = generate_choice_cam({
        'id_tg': ['=', message.from_user.id],
        'view_cam': ['=', message.text[2:]],
        'purpose': ['=', 'Уличные'],
        'type_cam': ['!=', 'IP']
    })
    name = camera.model.strip().replace('/', '').replace('\\', '')
    try:
        file = InputFile(os.path.join('commercial_proposal', 'images', 'camera', camera.brand, name + '.jpg'))
        await message.answer_photo(photo=file, caption=f'Будет использована камера:\n'
                                                       f'{camera.model}, {camera.description}\n'
                                                       f'Цена: {camera.price} руб.')
    except FileNotFoundError:
        await message.answer(text=f'Будет использована камера:\n'
                                  f'{camera.model}, {camera.description}\n'
                                  f'Цена: {camera.price} руб.')
    await state.update_data(type_cam_on_street=message.text)
    await state.update_data(data_cam_out=camera)
    await message.answer('Сколько дней хранить архив с камер видеонаблюдения?',
                         reply_markup=keyboards.key_cancel_to_video)
    await DataPollAnalog.next()


@dp.message_handler(state=DataPollAnalog.days_for_archive)
async def step_5(message: Message, state: FSMContext):
    if not message.text.isdigit() or message.text == '0':
        await message.answer('Вы не верно указали архив. Укажите число дней?',
                             reply_markup=keyboards.key_cancel_to_video)
        return
    await state.update_data(days_for_archive=message.text)
    data = await state.get_data()
    table_data = calculate_analog_kp.calculate_result(data=data, id_tg=message.from_user.id)
    if not table_data[0]:
        await message.answer(
            f'Слишком большой архив для данной конфигурации. Максимальный архив {int(table_data[1])} дн.',
            reply_markup=keyboards.key_cancel_to_video)
        return
    file_name, number_kp = create_doc.save_kp(table_data[0], table_data[1]['total'], message.from_user.id)

    await state.finish()
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
    await message.answer(text='КП готов, что дальше?', reply_markup=keyboards.menu)
    analytics.insert_data('kp')
    db.write_number_kp(message.from_user.id, number_kp=int(number_kp) + 1)
    await asyncio.sleep(5)
    os.remove(file_name)
