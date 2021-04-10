import asyncio
import os

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentTypes, InputFile
from aiogram.utils.exceptions import BotBlocked

import analytics
import config
import db
from commercial_proposal import create_doc
from keyboards import keyboards
from keyboards.inline_keybords import actions
from keyboards.support.support_keyboards import (
    create_keyboard,
    confirm_order,
    answer_of_provider,
    cancel_connection,
    keyboard_for_provider
)
from misc import dp


def create_text(number_order, user, full_name):
    text = f'Пользователь: {full_name}\n' \
           f'Город: {user.city}\n' \
           f'Телефон: {user.phone}\n' \
           f'Номер заказа: {number_order}\n\n' \
           f'Здравствуйте.Внимание! Отправьте ответ в течении 30 мин.' \
           f'Чтобы отправить ответ введите: нажмите кнопку "Ответить на заказ" и в следующих сообщениях, отправьте ' \
           f'информацию.\nПосле нажмите кнопку "Завершить отправку"' \
           f'С уважением,\nКоманда Rommo'
    return text


@dp.callback_query_handler(actions.filter(), state='send_kp')
async def send_kp_to_provider(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    user = db.get_data('name, phone, city, number_order', 'users', {'id_tg': ('=', call.from_user.id)})[0]
    number_order = f'{user.phone[-4:]}-{user.number_order + 1}'
    keyboard = keyboard_for_provider(call.from_user.id, number_order)
    text = create_text(number_order, user, call.from_user.full_name)
    file_name = create_doc.save_table_to_provider(data['to_provider'], number_order, call.from_user.id)
    file = InputFile(file_name)
    send = await dp.bot.send_document(chat_id=config.ADMIN_ID[0], caption=text, document=file,
                                      reply_markup=keyboard)
    answer = f"""
📦 Ваш заказ №{number_order} отправлен поставщикам.\n
❗️Обратите внимание, что некоторые материалы продаются кратно упаковке.\n
🧩 Данный функционал находится на этапе тестирования, время ожидания ответа поставщиков может превышать 30 мин.
"""
    await call.message.answer(text=answer, reply_markup=keyboards.menu)
    db.update_data('users', call.from_user.id, {'number_order': user.number_order + 1})
    analytics.insert_data('send_order')
    await state.finish()
    await asyncio.sleep(5)
    os.remove(file_name)


# @dp.callback_query_handler(actions.filter(), state='send_kp')
# async def send_kp_to_provider(call: CallbackQuery, callback_data: dict, state: FSMContext):
#     await call.answer(cache_time=60)
#     answer = callback_data.get('make')
#     if answer == 'No':
#         await state.finish()
#         await call.message.answer('Готово', reply_markup=keyboards.menu)
#         return
#     data = await state.get_data()
#     user = db.get_data('name, phone, city, number_order', 'users', {'id_tg': ('=', call.from_user.id)})[0]
#     number_order = f'{user.phone[-4:]}-{user.number_order + 1}'
#     keyboard = keyboard_for_provider(call.from_user.id, number_order)
#     text = create_text(number_order, user, call.from_user.full_name)
#     file_name = create_doc.save_table_to_provider(data['to_provider'], number_order, call.from_user.id)
#     providers = db.get_data('id_tg', 'users', {'is_provider': ('=', True), 'city': ('=', user.city)})
#     if not providers:
#         providers = db.get_data('id_tg', 'users', {'is_provider': ('=', True)})
#         if not providers:
#             await call.message.answer('Поставщиков пока нет')
#             return
#     flg = True
#     for provider in providers:
#         try:
#             if flg:
#                 file = InputFile(file_name)
#                 send = await dp.bot.send_document(chat_id=provider.id_tg, caption=text, document=file,
#                                                   reply_markup=keyboard)
#                 file_id = send.document.file_id
#                 flg = False
#             else:
#                 await dp.bot.send_document(chat_id=provider.id_tg, caption=text, document=file_id,
#                                            reply_markup=keyboard)
#         except BotBlocked:
#             pass
#     answer = f"""
# 📦 Ваш заказ №{number_order} отправлен поставщикам.\n
# ❗️Обратите внимание, что некоторые материалы продаются кратно упаковке.\n
# 🧩 Данный функционал находится на этапе тестирования, время ожидания ответа поставщиков может превышать 30 мин.
# """
#     await call.message.answer(text=answer, reply_markup=keyboards.menu)
#     db.update_data('users', call.from_user.id, {'number_order': user.number_order + 1})
#     analytics.insert_data('send_order')
#     await state.finish()
#     await asyncio.sleep(5)
#     os.remove(file_name)


@dp.message_handler(user_id=config.ADMIN_ID[0], commands=['answer'])
async def get_id_user(message: Message, state: FSMContext):
    data = message.text.split()
    await state.update_data({'user_id': data[1], 'number_order': data[-1] if len(data) == 3 else 'Неизвестен'})
    await message.answer('Введите ответ')
    await state.set_state('answer_to_user')


@dp.callback_query_handler(answer_of_provider.filter())
async def get_data_order(call: CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer()
    id_tg = callback_data.get('id_tg')
    number_order = callback_data.get('number_order')
    await state.update_data({'user_id': id_tg, 'number_order': number_order})
    await call.message.answer('Введите ответ', reply_markup=cancel_connection)
    await state.set_state('answer_to_user')


@dp.message_handler(state='answer_to_user', content_types=ContentTypes.ANY)
async def send_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    number_order = data.get('number_order')
    user_id = data.get('user_id')
    phone = db.get_data('phone', 'users', {'id_tg': ('=', message.from_user.id)})[0].phone
    if message.text == 'Закончить отправку':
        await dp.bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=data.get('message_id'),
            reply_markup=create_keyboard(phone, number_order, message.from_user.id)
        )
        await message.answer('Выберите действие', reply_markup=keyboards.menu)
        await state.finish()
        analytics.insert_data('send_answer')
        return
    message_info = await message.copy_to(chat_id=user_id)
    await state.update_data(message_id=message_info.message_id)


@dp.callback_query_handler(confirm_order.filter())
async def confirm_order(call: CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer()
    number_order = callback_data.get('number_order')
    phone = callback_data.get('phone')
    id_provider = callback_data.get('id_provider')
    answer = f"""
📦 Заказ №{number_order} зарезервирован для вас\n
📞 Свяжитесь с поставщиком для уточнения деталей по заказу. Тел: {phone}
"""
    await call.message.answer(answer)
    await dp.bot.send_message(chat_id=id_provider,
                              text=f'Заказ {number_order} от пользователя {call.from_user.id}: '
                                   f'{call.from_user.full_name} подтвержден')
    analytics.insert_data('confirm_order')
