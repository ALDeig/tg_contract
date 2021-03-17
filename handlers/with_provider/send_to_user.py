from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentTypes

import config
from keyboards.support.support_keyboards import create_keyboard, confirm_order
from misc import dp


@dp.message_handler(user_id=config.ADMIN_ID[0], commands=['answer'])
async def get_id_user(message: Message, state: FSMContext):
    data = message.text.split()
    await state.update_data({'user_id': data[1], 'number_order': data[-1] if len(data) == 3 else 'Неизвестен'})
    await message.answer('Введите ответ')
    await state.set_state('answer_to_user')


@dp.message_handler(state='answer_to_user', content_types=ContentTypes.ANY)
async def send_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    number_order = data.get('number_order')
    await message.copy_to(chat_id=user_id, reply_markup=create_keyboard(number_order))
    # await dp.bot.send_message(chat_id=user_id, text=message.text, reply_markup=create_keyboard(number_order))
    await state.finish()


@dp.callback_query_handler(confirm_order.filter())
async def confirm_order(call: CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer()
    number_order = callback_data.get('number_order')
    await call.message.answer(f'Заказ №{number_order} зарезервирован для вас.\nПредставитель поставщика свяжется с '
                              f'вами в бижайшее время для уточнения деталей по заказу.')
    await dp.bot.send_message(chat_id=config.ADMIN_ID[0],
                              text=f'Заказ {number_order} от пользователя {call.from_user.id}: '
                                   f'{call.from_user.full_name} подтвержден')
