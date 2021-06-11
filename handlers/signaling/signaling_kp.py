import asyncio
import os
from loguru import logger
from pathlib import Path

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InputFile, CallbackQuery, ReplyKeyboardMarkup

import analytics
import db
from keyboards import keyboards
from keyboards import signaling_kb
from keyboards.inline_keybords import inline_yes_or_no
from keyboards.selection_equipments import rec_selections_kbs
from keyboards.signaling_kb import create_kb_safe, callback_safe, floors_kb
from utils.signaling.calculate_signaling_kp import SignalingKp
from commercial_proposal import create_doc
from misc import dp


async def check_select_protection(choice_protection, msg, state):
    data = await state.get_data()
    if choice_protection['leakage_protection']:
        await msg.answer('Укажите количество ванных комнат включая кухню', reply_markup=keyboards.key_cancel)
        await state.set_state('number_bedrooms')
    elif choice_protection['street_guard']:
        await msg.answer('Укажите площадь участка кв.м', reply_markup=keyboards.key_cancel)
        await state.set_state('area_apartment')
    else:
        text = send_now_equipments(data, msg.from_user.id)
        await msg.answer(text=text)
        await msg.answer('Усилить защиту?', reply_markup=keyboards.yes_or_no)
        await state.set_state('strengthen_protection')


def send_now_equipments(data, user_id):
    rows, cost_work, cost_equipment, to_provider = SignalingKp(data, user_id).main()
    result = dict()
    for key, value in rows.items():
        if key == 'row_2':
            break
        if key == 'row_1':
            continue
        result[value[0]] = value[2]
    text = 'Текущее оборудование:\n'
    for key, value in result.items():
        text += f'{key}: {value}\n'
    return text


@dp.message_handler(state='brand_signaling')
async def step_1(msg: Message, state: FSMContext):
    choice_protection = {
        'intrusion_protection': 0,
        'fire_safety': 0,
        'leakage_protection': 0,
        'street_guard': 0
    }
    await state.update_data(choice_protection=choice_protection)
    keyboard = create_kb_safe(choice_protection)
    await msg.answer('Какая защита нужна?', reply_markup=keyboard)
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True).add('👍 Завершить выбор', '↩️Отмена')
    await msg.answer('Нажмите "👍 Завершить выбор", чтобы закончить выбор', reply_markup=keyboard)
    await state.set_state('signaling_2')


@dp.callback_query_handler(callback_safe.filter(), state='signaling_2')
async def get_type_security(call: CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer()
    data = await state.get_data()
    choice_protection = data.get('choice_protection')
    choice_protection[callback_data.get('security_type')] = 0 if callback_data.get('value') == '1' else 1
    await state.update_data(choice_protection=choice_protection)
    inline_keyboard = create_kb_safe(choice_protection)
    await call.message.edit_reply_markup(inline_keyboard)


@dp.message_handler(text='👍 Завершить выбор', state='signaling_2')
async def step_2(msg: Message, state: FSMContext):
    data = await state.get_data()
    choice_protection = data.get('choice_protection')
    if choice_protection['intrusion_protection']:
        await msg.answer('Укажите количество комнат, включая кухню', reply_markup=keyboards.key_cancel)
        await state.set_state('number_rooms')
    elif choice_protection['fire_safety']:
        await msg.answer('Укажите количество комнат, включая кухню', reply_markup=keyboards.key_cancel)
        await state.set_state('number_rooms_for_fire')
    elif choice_protection['leakage_protection']:
        await msg.answer('Укажите количество ванных комнат', reply_markup=keyboards.key_cancel)
        await state.set_state('number_bedrooms')
    elif choice_protection['street_guard']:
        await msg.answer('Укажите площадь участка кв.м', reply_markup=keyboards.key_cancel)
        await state.set_state('area_apartment')


@dp.message_handler(state='number_rooms')
async def step_3(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer('Введите количество комнат', reply_markup=keyboards.key_cancel)
        return
    await state.update_data(rooms=msg.text)
    await msg.answer('Укажите этаж квартиры', reply_markup=floors_kb)
    await state.set_state('apartment_floor')


@dp.message_handler(state='number_rooms_for_fire')
async def get_number_rooms_for_fire(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer('Введите количество комнат', reply_markup=keyboards.key_cancel)
        return
    await state.update_data(rooms=msg.text)
    data = await state.get_data()
    choice_protection = data.get('choice_protection')
    await check_select_protection(choice_protection, msg, state)


@dp.message_handler(state='apartment_floor')
async def step_4(msg: Message, state: FSMContext):
    floors = ["Первый", "Второй", "Последний", "Другой"]
    if msg.text not in floors:
        await msg.answer('Выберите вариант')
        return
    await state.update_data(floor=msg.text)
    data = await state.get_data()
    choice_protection = data.get('choice_protection')
    await check_select_protection(choice_protection, msg, state)


@dp.message_handler(state='number_bedrooms')
async def get_number_bedrooms(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer('Укажите количество ванных комнат', reply_markup=keyboards.key_cancel)
        return
    await state.update_data(bedrooms=msg.text)
    data = await state.get_data()
    if data['choice_protection']['street_guard']:
        await msg.answer('Укажите площадь участка в кв.м', reply_markup=keyboards.key_cancel)
        await state.set_state('area_apartment')
    else:
        text = send_now_equipments(data, msg.from_user.id)
        await msg.answer(text=text)
        await msg.answer('Усилить защиту?', reply_markup=keyboards.yes_or_no)
        await state.set_state('strengthen_protection')


@dp.message_handler(state='area_apartment')
async def get_area_apartment(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer('Укажите площадь', reply_markup=keyboards.key_cancel)
        return
    data = await state.get_data()
    await state.update_data(area_apartment=msg.text)
    text = send_now_equipments(data, msg.from_user.id)
    await msg.answer(text=text)
    await msg.answer('Усилить защиту?', reply_markup=keyboards.yes_or_no)
    await state.set_state('strengthen_protection')


async def send_kp(data: dict, msg: Message, state: FSMContext):
    data, cost_work, cost_equipment, to_provider = SignalingKp(data, msg.from_user.id).main()
    list_rows = list(data.values())
    file_name, number_kp = create_doc.save_kp(list_rows, cost_work + cost_equipment, msg.from_user.id, signaling=True)
    file = InputFile(file_name)
    await asyncio.sleep(3)
    await msg.answer(text='КП готов', reply_markup=keyboards.go_menu)
    await msg.answer_document(document=file)
    analytics.insert_data('signaling_kp')
    # await state.finish()
    text = """✅ Коммерческое предложение готово!\n
📦 Закажи оборудование из КП в 1 клик через бот!\n
🎁 Получи скидку!\n
👇Жми «Заказать оборудование»"""
    await msg.answer(text=text, reply_markup=inline_yes_or_no)
    await state.set_state('send_kp')
    await state.update_data({'file': file_name, 'to_provider': to_provider, 'signaling': True})
    logger.info(f'File name is - {file_name}')
    await asyncio.sleep(5)
    db.write_number_kp(id_tg=msg.from_user.id, number_kp=int(number_kp) + 1)
    os.remove(file_name)


@dp.message_handler(state='strengthen_protection')
async def get_strengthen_protection(msg: Message, state: FSMContext):
    if msg.text == '✅Да':
        await msg.answer('Какую защиту добавить?', reply_markup=signaling_kb.additional_devices_kb)
        await state.set_state('add_devices')
        return
    data = await state.get_data()
    await send_kp(data, msg, state)


@dp.message_handler(text='Сформировать КП', state='add_devices')
async def create_kp(msg: Message, state: FSMContext):
    data = await state.get_data()
    await send_kp(data, msg, state)


@dp.message_handler(text='↩ ️Отмена', state='add_devices')
async def back_step(msg: Message, state: FSMContext):
    await msg.answer('Какую защиту добавить?', reply_markup=signaling_kb.additional_devices_kb)


@dp.message_handler(state='add_devices')
async def add_devices(msg: Message, state: FSMContext):
    tables = {
        'Защита от вторжения': 'invasion',
        'Пожарная безопасность': 'fire',
        'Защита от протечек': 'leak',
        'Сирены': 'siren',
        'Управление': 'control',
        'Автоматизация': 'automation',
        'Ретрансляторы': 'hub'
    }
    if msg.text not in tables.keys():
        return
    if msg.text == 'Ретрансляторы':
        filters = {'name': ('=', 'ReX')}
    else:
        filters = None
    devices = db.get_data('name, short_name, price', tables.get(msg.text), filters=filters)
    await state.update_data(table=tables.get(msg.text))
    await msg.answer(
        text='Выберите вариант',
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add('↩ ️Отмена')
    )
    for device in devices:
        keyboard = rec_selections_kbs.create_inline_keyboard_2(device.name)
        text = f'{device.name} {device.short_name}\nЦена: {device.price}'
        try:
            name = device.name.strip().replace('/', '').replace('\\', '').replace(' ', '') + '.jpg'
            # await msg.answer('Укажите количество')
            file = InputFile(Path() / 'commercial_proposal' / 'images' / 'signaling' / tables[msg.text] / 'Ajax' / name)
            await msg.answer_photo(photo=file, caption=text, reply_markup=keyboard)
        except Exception as er:
            logger.error(er)
            await msg.answer(
                text=text,
                reply_markup=keyboard
            )


@dp.callback_query_handler(rec_selections_kbs.choice_reg_callback.filter(), state='add_devices')
async def choice_device(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    model = callback_data.get('model')
    if 'add_devices' not in data:
        await state.update_data(add_devices={})
    await state.update_data(model=model)
    await call.message.answer('Укажите количество')
    await state.set_state('get_number')


@dp.message_handler(state='get_number')
async def get_number(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer('Укажите количество')
        return
    data = await state.get_data()
    table = data.get('table')
    add_device = data['add_devices']
    model = data['model']
    add_device[table] = (model, int(msg.text))
    await state.update_data(add_devices=add_device)
    await msg.answer('Какую защиту добавить?', reply_markup=signaling_kb.additional_devices_kb)
    await state.set_state('add_devices')


# async def get_strengthen_protection(msg: Message, state: FSMContext):
#     if msg.text == '✅Да':
# @dp.message_handler(state='strengthen_protection')
# async def get_strengthen_protection(msg: Message, state: FSMContext):
#     if msg.text == '✅Да':
#         additional_devices = {
#             'intrusion_protection': 0,
#             'fire_safety': 0,
#             'leakage_protection': 0,
#             'siren': 0,
#             'control': 0,
#             'automation': 0,
#             'repeaters': 0
#         }
#         await state.update_data(add_devices=additional_devices)
#         keyboard = create_kb_additional_devices(additional_devices)
#         await msg.answer('Какие устройства добавить?', reply_markup=keyboard)
#         keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add('Завершить выбор')
#         await msg.answer('Нажмите "Завершить выбор", чтобы закончить выбор', reply_markup=keyboard)
#         await state.set_state('add_devices')
#     elif msg.text == '❌Нет':
#         data = await state.get_data()
#         rows_kp = SignalingKp(data, msg.from_user.id).main()
#         list_rows = list(rows_kp[0].values())
#         file_name, number_kp = create_doc.save_kp(list_rows, rows_kp[1] + rows_kp[2], msg.from_user.id)
#         file = InputFile(file_name)
#         await msg.answer(text='КП готов', reply_markup=keyboards.go_menu)
#         await msg.answer_document(document=file)
#         await asyncio.sleep(5)
#         os.remove(file_name)
#
#
# @dp.callback_query_handler(callback_devices.filter(), state='add_devices')
# async def get_add_devices(call: CallbackQuery, state: FSMContext, callback_data: dict):
#     await call.answer()
#     data = await state.get_data()
#     add_devices = data.get('add_devices')
#     add_devices[callback_data.get('security_type')] = 0 if callback_data.get('value') == '1' else 1
#     await state.update_data(add_devices=add_devices)
#     inline_keyboard = create_kb_additional_devices(add_devices)
#     await call.message.edit_reply_markup(inline_keyboard)
#
#
# def create_messages(devices):
#     tables = {
#         'intrusion_protection': 'invasion',
#         'fire_safety': 'fire',
#         'leakage_protection': 'leak',
#         'siren': 'siren',
#         'control': 'control',
#         'automation': 'automation',
#         'repeaters': ''}
#
#
# @dp.message_handler(text='Завершить выбор', state='add_devices')
# async def step_5(msg: Message, state: FSMContext):
#     data = await state.get_data()
#     print(data.get('add_devices'))
#     devices = [key for key, value in data.get('add_devices').items() if value == 1]
#     print(devices)
