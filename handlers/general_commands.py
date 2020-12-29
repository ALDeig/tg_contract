import os

import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import BotBlocked

import analytics
import config
import db
from commercial_proposal.gsheets import sheets
from misc import dp, bot
import keyboards
from work_with_api import get_limit_api_inn, get_limit_api_bik

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
    tpl = State()
    del_rev = State()
    num_rev = State()


class CreateKP(StatesGroup):
    start = State()


class MessageFromUsers(StatesGroup):
    message = State()


@dp.message_handler(text='↩️Отмена', state='*')
@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработка команды старт"""
    await state.finish()
    if not db.check_user_in(message.from_user.id, 'id_tg', 'users'):  # Если пользователя нет в базе.
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add('Регистрация')
        await message.answer(text=start_message, parse_mode='HTML', reply_markup=keyboard)
    else:
        await message.answer('Выберите действие', reply_markup=keyboards.menu)


@dp.message_handler(commands='get_analytics', user_id=config.ADMIN_ID)
async def cmd_get_analytics(message: types.Message):
    data = analytics.get_analytics()
    count_users = db.get_count_users()
    count_executors = db.get_count_executors()

    await message.answer(f"<b>Пользователей:</b> {count_users}\n"
                         f"<b>Исполнителей:</b> {count_executors}\n"
                         f"<b>Договоров:</b> {data['contract']}\n"
                         f"<b>Шаблоны КП:</b> {data['template']}\n"
                         f"<b>КП:</b> {data['kp']}\n"
                         f"<b>ИНН:</b> {data['request_inn']}\n"
                         f"<b>БИК:</b> {data['request_bik']}", parse_mode='HTML')


@dp.message_handler(commands='get_reviews', user_id=config.ADMIN_ID)
async def send_all_reviews(message: types.Message):
    reviews = db.get_reviews_with_id()
    text = 'Отзывы: \n'
    for review in reviews:
        text += f'{review[0]}. {review[1]}\n'

    await Document.del_rev.set()
    await message.answer(text, reply_markup=keyboards.del_review)


@dp.message_handler(Command('get_limit'), user_id=config.ADMIN_ID)
async def send_limits(message: types.Message):
    inn = get_limit_api_inn()
    bik = get_limit_api_bik()
    if not inn or not bik:
        await message.answer('Ошибка')
        return
    await message.answer(f'ИНН:\n'
                         f'Лимит: {inn[0]}\n'
                         f'Потрачено: {inn[1]}\n'
                         f'Осталось: {inn[2]}\n'
                         f'Дата окончания: {inn[3]}')
    await message.answer(f'БИК:\n'
                         f'Лимит: {bik[0]}\n'
                         f'Потрачено: {bik[1]}\n'
                         f'Осталось: {bik[2]}\n'
                         f'Дата окончания: {inn[3]}')


@dp.message_handler(text='Удалить отзыв', user_id=config.ADMIN_ID, state=Document.del_rev)
async def del_review(message: types.Message, state: FSMContext):
    await Document.num_rev.set()
    await message.answer('Отправьте номер отзыва на удаление')


@dp.message_handler(user_id=config.ADMIN_ID, state=Document.num_rev)
async def get_num_review(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Неверный номер')
    db.del_review(message.text)
    await state.finish()
    await message.answer('Отзыв удален')


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


@dp.message_handler(text='🎥 Видеонаблюдение')
async def send_menu_video(message: types.Message):
    await message.answer('Выбери действие', reply_markup=keyboards.menu_video)


@dp.message_handler(text='💰 Коммерческие предложение')  # , state=CreateKP.start
async def create_kp(message: types.Message, state: FSMContext):
    await message.answer(text='Выбери действие', reply_markup=keyboards.menu_kp)
    # await state.finish()


@dp.message_handler(text='🎛 Изменить данные', state='*')
async def change_data(message: types.Message):
    await message.answer(text='Выберите действие', reply_markup=keyboards.choice_menu)


@dp.message_handler(text='📤 Загрузить шаблон КП', state='*')
async def add_tpl_kp(message: types.Message):
    await message.answer('Отправьте файл шаблона', reply_markup=keyboards.key_cancel)
    await Document.tpl.set()


@dp.message_handler(content_types=types.ContentTypes.DOCUMENT, state=Document.tpl)
async def download_file(message: types.Message, state: FSMContext):
    name_file = await message.document.download()
    old_tpl = db.get_kp_tpl(message.from_user.id)
    if old_tpl is not None:
        os.remove(old_tpl)
    db.insert_kp_tpl(name_file.name, message.from_user.id)
    await state.finish()
    await message.answer('Шаблон загружен')
    analytics.insert_data('template')


@dp.message_handler(Command('send_message'), user_id=config.ADMIN_ID, state='*')
async def send_message_all_users(message: types.Message):
    await message.answer('Отправь сообщение', reply_markup=keyboards.key_cancel)
    await MessageFromUsers.message.set()


@dp.message_handler(user_id=config.ADMIN_ID, state=MessageFromUsers.message)
async def send_message_all_users_2(message: types.Message, state: FSMContext):
    users = db.get_users()
    for user in users:
        try:
            await bot.send_message(chat_id=user[0], text=message.text)
        except BotBlocked:
            pass
    await state.finish()


@dp.message_handler(Command('save_cameras'), user_id=config.ADMIN_ID)
async def save_info(message: types.Message):
    data = sheets.get_info_of_cameras()
    columns = ('country', 'currency', 'provider', 'brand', 'type_cam', 'model', 'price', 'trade_price', 'view_cam',
               'purpose', 'ppi', 'specifications', 'description', 'image')
    db.insert_data_of_cameras(data=data, column=columns)
    await message.answer('Готово')
