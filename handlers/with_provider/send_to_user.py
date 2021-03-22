from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentTypes

import analytics
import config
import db
from keyboards.support.support_keyboards import create_keyboard, confirm_order, answer_of_provider
from misc import dp


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
    await call.message.answer('Введите ответ')
    await state.set_state('answer_to_user')


@dp.message_handler(state='answer_to_user', content_types=ContentTypes.ANY)
async def send_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    phone = db.get_data('phone', 'users', {'id_tg': ('=', message.from_user.id)})[0].phone
    number_order = data.get('number_order')
    await message.copy_to(chat_id=user_id, reply_markup=create_keyboard(phone, number_order, message.from_user.id))
    analytics.insert_data('send_answer')
    # await dp.bot.send_message(chat_id=user_id, text=message.text, reply_markup=create_keyboard(number_order))
    await state.finish()


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
