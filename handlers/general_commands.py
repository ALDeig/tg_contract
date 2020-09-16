from aiogram import types
from aiogram.dispatcher import FSMContext

import analytics
import config
import db
from misc import dp


start_message = """ Отлично! Для начала надо зарегистрироваться тебе, как пользователю системы и зарегистрировать свою \
фирму исполнителя (подготовь ИНН, БИК банка и номер расчетного счёта). Эти данные я буду хранить, вводить их каждый \
раз не надо, но у тебя всегда будет возможность изменить их. После регистрации исполнителя, можно перейти к \
формированию договора, отвечай на мои вопросы про твоего клиента (подготовь ИНН, БИК банка и номер расчетного счёта) и \
другие детали договора. Сам договор будет храниться в нашей переписке, его можно отправить клиенту на почту на подпись \
или для редактирования. 
<b>Поехали!</b>
"""


@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработка команды старт"""
    await state.finish()
    if not db.check_user_in(message.from_user.id, 'id_tg', 'users'):  # Если пользователя нет в базе.
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add('Регистрация')
        await message.answer(text=start_message, parse_mode='HTML', reply_markup=keyboard)
    elif not db.check_user_in(message.from_user.id, 'user_id_tg', 'executor_ip') \
            and not db.check_user_in(message.from_user.id, 'user_id_tg', 'executor_ooo'):  # Если у пользователя нет исполн.
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add('Регистрация исполнителя')
        await message.answer('Зарегистрируйте исполнителя', reply_markup=keyboard)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Договор на монтаж видеонаблюдения')
        keyboard.add('Изменить реквизиты исполнителя')
        keyboard.add('Изменить свои данные')
        await message.answer('Выберите действие', reply_markup=keyboard)


@dp.message_handler(commands='get_analytics', user_id=config.ADMIN_ID)
async def cmd_get_analytics(message: types.Message):
    data = analytics.get_analytics()
    count_users = db.get_count_users()
    count_executors = db.get_count_executors()

    await message.answer(f"<b>Количество пользователей:</b> {count_users}\n"
                         f"<b>Количество исполнителей:</b> {count_executors}\n"
                         f"<b>Количество отправленных договоров:</b> {data['contract']}\n"
                         f"<b>Количество запросов по ИНН:</b> {data['request_inn']}\n"
                         f"<b>Количество запросов по БИК:</b> {data['request_bik']}", parse_mode='HTML')
