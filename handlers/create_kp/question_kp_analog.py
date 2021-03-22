import asyncio
import os

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InputFile, ReplyKeyboardRemove, CallbackQuery
from aiogram.utils.exceptions import BotBlocked

import analytics
import config
import db
from keyboards.create_kp.analog_kp_keyboard import create_keyboard_kp
from keyboards import keyboards
from keyboards.inline_keybords import actions, inline_yes_or_no
from keyboards.support.support_keyboards import keyboard_for_provider
from commercial_proposal.analog_kp import calculate_analog_kp
from commercial_proposal import create_doc
from handlers.questions_of_kp import DataPoll
from misc import dp
from states.analog_kp import PricesAnalogKp, DataPollAnalog


# from utils.gmail.sendMessage import send_message


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
    await message.answer(text='КП готов', reply_markup=keyboards.go_menu)
    await message.answer_document(document=file)
    text = """
📦 Можно отправить поставщикам из вашего города оборудование и материалы из КП, что бы получить ценовое \
предложение на закупку. Нажмите кнопку «Отправить»👇\n
🛡 Обращаем внимание, что поставщики получат только количество оборудования и материалов. Стоимость работ и цена \
оборудования из КП не разглашаются.
"""
    await message.answer(text=text, reply_markup=inline_yes_or_no)
    old_tpl = db.get_kp_tpl(message.from_user.id)
    if not old_tpl:
        await message.answer(text='Загрузите свой шаблон КП:  https://clck.ru/S8SjN.', disable_web_page_preview=True)
    # await message.answer(text='КП готов, что дальше?', reply_markup=keyboards.menu)
    # await message.answer(text='КП готов. Отправьте поставщику, чтобы получить предложение.\nОтправить?',
    #                      reply_markup=keyboards.yes_or_no)
    await state.update_data({'file': file_name, 'to_provider': table_data[-1]})
    await DataPollAnalog.send_kp.set()
    analytics.insert_data('kp')
    db.write_number_kp(message.from_user.id, number_kp=int(number_kp) + 1)
    # await state.finish()
    # return
    await asyncio.sleep(5)
    os.remove(file_name)


@dp.callback_query_handler(actions.filter(), state=DataPollAnalog.send_kp)
async def send_kp_to_provider(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=30)
    answer = callback_data.get('make')
    if answer == 'No':
        await state.finish()
        await call.message.answer('Готово', reply_markup=keyboards.menu)
        return
    data = await state.get_data()
    user = db.get_data('name, phone, city, number_order', 'users', {'id_tg': ('=', call.from_user.id)})[0]
    number_order = f'{user.phone[-4:]}-{user.number_order + 1}'
    keyboard = keyboard_for_provider(call.from_user.id, number_order)
    text = f'Пользователь: {call.from_user.full_name}, ID: {call.from_user.id}\n' \
           f'Имя в базе: {user.name}\n' \
           f'Город: {user.city}\n' \
           f'Номер заказа: {number_order}\n\n' \
           f'Здравствуйте.Внимание! Отправьте ответ в течении 30 мин.' \
           f'Подтвердите наличие и укажите стоимость запрашиваемого оборудования в файле.\n' \
           f'Чтобы отправить ответ введите: нажмите кнопку "Ответить на заказ" и следующем сообщением, отправьте ' \
           f'информацию' \
           f'С уважением,\nКоманда Rommo'
    file_name = create_doc.save_table_to_provider(data['to_provider'], number_order, call.from_user.id)
    file = InputFile(file_name)
    answer = f"""
📦 Ваш заказ №{number_order} отправлен поставщикам.\n
❗️Обратите внимание, что некоторые материалы продаются кратно упаковке.\n
🧩 Данный функционал находится на этапе тестирования, время ожидания ответа поставщиков может превышать 30 мин.
"""
    await call.message.answer(text=answer, reply_markup=keyboards.menu)
    # send_message(text, file_name, 'alkin.denis@gmail.com', 'Новый заказ от RommoBot')
    providers = db.get_data('id_tg', 'users', {'is_provider': ('=', True), 'city': ('=', user.city)})
    if not providers:
        await call.message.answer('В вашем городе нет поставщиков')
        return
    for provider in providers:
        try:
            await dp.bot.send_document(chat_id=provider.id_tg, caption=text, document=file, reply_markup=keyboard)
        except BotBlocked:
            pass
    db.update_data('users', call.from_user.id, {'number_order': user.number_order + 1})
    analytics.insert_data('send_order')
    await state.finish()
    await asyncio.sleep(5)
    os.remove(file_name)


# @dp.message_handler(state=DataPollAnalog.send_kp)
# async def send_kp_to_provider(message: Message, state: FSMContext):
#     data = await state.get_data()
#     if message.text == 'Да':
#         user = db.get_data('name, phone, city, number_order', 'users', {'id_tg': ('=', message.from_user.id)})[0]
#         text = f'Пользователь: {message.from_user.full_name}, ID: {message.from_user.id}\n' \
#                f'Имя в базе: {user.name}\n' \
#                f'Телефон: {user.phone}\n' \
#                f'Город: {user.city}\n\n' \
#                f'Здравствуйте.Внимание! Отправьте ответ в течении 30 мин.' \
#                f'Подтвердите наличие и укажите стоимость запрашиваемого оборудования в файле.\n' \
#                f'С уважением,\nКоманда Rommo'
#         number_order = f'{user.phone[-4:]}-{user.number_order + 1}'
#         file_name = create_doc.save_table_to_provider(data['to_provider'], number_order, message.from_user.id)
#         file = InputFile(file_name)
#         await message.answer(f'Ваш заказ №{number_order} отправлен поставщикам. Ожидайте ответ в течении 30 мин. '
#                              'Обратите внимание, что некоторые материалы продаются кратно упаковке. '
#                              'Если вы ожидаете ответ дольше 30 мин, напишите “@RommoSupport” номер заказа.',
#                              reply_markup=keyboards.menu)
#         # send_message(text, file_name, 'alkin.denis@gmail.com', 'Новый заказ от RommoBot')
#         await dp.bot.send_document(chat_id=config.ADMIN_ID[0], caption=text, document=file)
#         db.update_data('users', message.from_user.id, {'number_order': user.number_order + 1})
#         await asyncio.sleep(5)
#         os.remove(file_name)
#     else:
#         await message.answer('Готово!', reply_markup=keyboards.menu)
#     await state.finish()
