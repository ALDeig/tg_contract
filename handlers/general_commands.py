import os

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
from keyboards import keyboards
from work_with_api import get_limit_api_inn, get_limit_api_bik

start_message = "Отлично!\n\nНадо пройти небольшую регистрацию. Всего 3 вопроса.\n\nЖми кнопку <b>Регистрация👇</b>."


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


@dp.message_handler(text='↩Отмена', state='*')
@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработка команды старт внутри некоторых функций"""
    await state.finish()
    if not db.check_user_in(message.from_user.id, 'id_tg', 'users'):  # Если пользователя нет в базе.
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add('Регистрация')
        await message.answer(text=start_message, parse_mode='HTML', reply_markup=keyboard)
    else:
        await message.answer('Выберите действие', reply_markup=keyboards.menu_video)


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


@dp.message_handler(text='💰 Коммерческие предложения')  # , state=CreateKP.start
async def create_kp(message: types.Message, state: FSMContext):
    await message.answer(text='Выбери действие', reply_markup=keyboards.menu_kp)
    # await state.finish()


@dp.message_handler(text='🎛 Изменить данные', state='*')
async def change_data(message: types.Message):
    await message.answer(text='Выберите действие', reply_markup=keyboards.choice_menu)


@dp.message_handler(text='📤 Загрузить шаблон КП', state='*')
async def add_tpl_kp(message: types.Message):
    await message.answer('Инструкция, как использовать свой шаблон - https://clck.ru/S8SjN\n'
                         '\nОтправьте мне файл шаблона с вашими контактами👇', reply_markup=keyboards.key_cancel)
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


def save_data():
    try:
        camera = sheets.get_info(0, 'camera', 12)
        columns = ('country', 'currency', 'provider', 'brand', 'type_cam', 'model', 'price', 'view_cam',
                   'purpose', 'ppi', 'specifications', 'description', 'image', 'box')
        db.insert_data_of_equipments(data=camera, column=columns, table='data_cameras')
        del camera
        print('Cameras done')
        recorder = sheets.get_info(1, 'recorder', 13)
        columns = ('country', 'currency', 'provider', 'brand', 'type_recorder', 'model', 'price', 'number_channels',
                   'number_hdd', 'max_size_hdd', 'number_poe', 'specifications', 'description', 'image')
        db.insert_data_of_equipments(data=recorder, column=columns, table='DataRecorder')
        del recorder
        print('Recorder done')
        hdd = sheets.get_info(2, 'hdd')
        columns = ('country', 'currency', 'provider', 'brand', 'memory_size', 'model', 'price', 'trade_price', 'serial',
                   'type_hdd', 'interface', 'description', 'image')
        db.insert_data_of_equipments(data=hdd, column=columns, table='DataHDD')
        del hdd
        print('HDD done')
        switch = sheets.get_info(3, 'switch', 11)
        columns = (
            'country', 'currency', 'provider', 'brand', 'number_ports', 'model', 'price', 'ports_poe',
            'power', 'specifications', 'description', 'image')
        db.insert_data_of_equipments(data=switch, column=columns, table='DataSwitch')
        del switch
        print('Switch done')
        box = sheets.get_info(4, 'box')
        columns = ('country', 'currency', 'provider', 'brand', 'number_units', 'model', 'price', 'trade_price',
                   'mounting_type', 'dimensions', 'specifications', 'description', 'image')
        db.insert_data_of_equipments(data=box, column=columns, table='DataBox')
        del box
        print('Box done')
        ibp = sheets.get_info(5, 'IBP')
        columns = (
            'country', 'currency', 'provider', 'brand', 'model', 'power', 'price', 'trade_price', 'mounting_type',
            'profile', 'specifications', 'description', 'image')
        db.insert_data_of_equipments(data=ibp, column=columns, table='DataIBP')
        print('IBP done')
        del ibp
        cable = sheets.get_info(6, 'cable')
        columns = ('country', 'currency', 'provider', 'type_cable', 'type_system', 'brand', 'model', 'price', 'trade_price', 'use',
                   'specifications', 'description', 'image')
        db.insert_data_of_equipments(cable, columns, 'DataCable')
        print('Cable done')
        bracing = sheets.get_info(7, 'bracing', 10)
        columns = ('country', 'currency', 'provider', 'brand', 'model', 'price', 'trade_price', 'mount_type',
                   'specifications', 'description', 'image')
        db.insert_data_of_equipments(bracing, columns, 'DataBracing')
    except Exception as e:
        print(e)
        return

    return True


@dp.message_handler(Command('save_cameras'), user_id=config.ADMIN_ID)
async def save_info(message: types.Message):
    await message.answer('Я начал сохранять информацию')
    # data = sheets.get_info(1, 'camera')
    # columns = ('country', 'currency', 'provider', 'brand', 'type_cam', 'model', 'price', 'trade_price', 'view_cam',
    #            'purpose', 'ppi', 'specifications', 'description', 'image')
    # db.insert_data_of_cameras(data=data, column=columns)
    result = save_data()
    if result:
        await message.answer('Готово')
    else:
        await message.answer('Ошибка сохранения')
