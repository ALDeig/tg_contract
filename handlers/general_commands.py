import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import analytics
import config
import db
from misc import dp
import keyboards

start_message = """ Отлично! Для начала надо зарегистрироваться тебе, как пользователю системы и зарегистрировать свою \
фирму исполнителя (подготовь ИНН, БИК банка и номер расчетного счёта). Эти данные я буду хранить, вводить их каждый \
раз не надо, но у тебя всегда будет возможность изменить их. После регистрации исполнителя, можно перейти к \
формированию договора, отвечай на мои вопросы про твоего клиента (подготовь ИНН, БИК банка и номер расчетного счёта) и \
другие детали договора. Сам договор будет храниться в нашей переписке, его можно отправить клиенту на почту на подпись \
или для редактирования. 
<b>Поехали!</b>
"""


class Document(StatesGroup):
    text_documents = State()


@dp.message_handler(text='↩️Отмена', state='*')
@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработка команды старт"""
    await state.finish()
    if not db.check_user_in(message.from_user.id, 'id_tg', 'users'):  # Если пользователя нет в базе.
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add('Регистрация')
        await message.answer(text=start_message, parse_mode='HTML', reply_markup=keyboard)
    # elif not db.check_user_in(message.from_user.id, 'user_id_tg', 'executor_ip') \
    #         and not db.check_user_in(message.from_user.id, 'user_id_tg', 'executor_ooo'):  # Если у пользователя нет исп
    #     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add('Регистрация исполнителя')
    #     await message.answer('Зарегистрируйте исполнителя', reply_markup=keyboard)
    else:
        await message.answer('Выберите действие', reply_markup=keyboards.menu)


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


@dp.message_handler(commands='document', user_id=config.ADMIN_ID)
async def create_text_for_document(message: types.Message):
    await message.answer('Отправь текст', reply_markup=keyboards.key_cancel)
    await Document.first()


@dp.message_handler(state=Document.text_documents, user_id=config.ADMIN_ID)
async def get_text_for_documents(message: types.Message, state: FSMContext):
    with open(os.path.join('db', 'document.txt'), 'w', encoding='UTF-8') as file:
        file.write(message.text)
    await message.answer('Текст записан')
    await state.finish()


@dp.message_handler(text='🗃 Документы')
async def send_documents(message: types.Message):
    try:
        with open(os.path.join('db', 'document.txt'), 'r', encoding='UTF-8') as file:
            text = file.read()
    except FileNotFoundError:
        await message.answer('Документов нет', reply_markup=keyboards.key_cancel)
        return
    await message.answer(text)


@dp.message_handler(text='💰 Создать КП', state='*')
async def create_kp(message: types.Message):
    await message.answer(text='Выбери действие', reply_markup=keyboards.menu_kp)


@dp.message_handler(text='🎛 Изменить данные', state='*')
async def change_data(message: types.Message):
    await message.answer(text='Выберите действие', reply_markup=keyboards.choice_menu)
