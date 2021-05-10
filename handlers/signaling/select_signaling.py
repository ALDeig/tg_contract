from pathlib import Path

from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.exceptions import BadRequest
from loguru import logger

import db
from keyboards import keyboards
from keyboards import signaling_kb
from keyboards.selection_equipments import rec_selections_kbs
from misc import dp
from handlers.select_equipment.start_selections import Selections


@dp.message_handler(text='⚙️Подбор оборудования', state='signaling_menu')
async def start_selections(msg: Message, state: FSMContext):
    await msg.answer(
        text='Какое оборудование подобрать?',
        reply_markup=signaling_kb.devices_selection
    )
    await state.set_state('selection_devices')


@dp.message_handler(state='selection_devices')
async def send_devices(msg: Message, state: FSMContext):
    tables = {'Хаб': 'hub', 'Вторжение': 'invasion', 'Пожар': 'fire', 'Протечка': 'leak', 'Сирена': 'siren',
              'Управление': 'control', 'ББП': 'bbp'}
    if msg.text not in tables:
        return
    if msg.text == 'Вторжение':
        keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True).add('Внутрений', 'Уличный', '↩️Отмена')
        await msg.answer('Выберите вариант', reply_markup=keyboard)
        await state.set_state('invasion_type')
        return
    columns = 'name, price' if msg.text == 'Хаб' else 'name, type, price'
    await state.update_data(table=msg.text)
    devices = db.get_data(columns, tables.get(msg.text))
    for device in devices:
        keyboard = rec_selections_kbs.create_inline_keyboard_2(device.name)
        if msg.text == 'Хаб':
            text = f'{device.name}\nЦена: {device.price}'
        else:
            text = f'{device.name}\nТип: {device.type}\nЦена: {device.price}'
        try:
            name = device.name.strip().replace('/', '').replace('\\', '').replace(' ', '') + '.jpg'
            file = InputFile(Path() / 'commercial_proposal' / 'images' / 'signaling' / tables[msg.text] / 'Ajax' / name)
            await msg.answer_photo(photo=file, caption=text, reply_markup=keyboard)
        except Exception as er:
            logger.error(er)
            await msg.answer(
                text=text,
                reply_markup=keyboard)
    await state.set_state('choice_device')


@dp.message_handler(state='invasion_type')
async def invasion_type(msg: Message, state: FSMContext):
    if msg.text not in ('Внутрений', 'Уличный', '↩️Отмена'):
        return
    devices = db.get_data('name, price', 'Invasion', {'installation': ('=', msg.text)})
    for device in devices:
        keyboard = rec_selections_kbs.create_inline_keyboard_2(device.name)
        await msg.answer(
            text=f'{device.name}\nЦена: {device.price}',
            reply_markup=keyboard)
    await state.set_state('choice_device')


@dp.callback_query_handler(rec_selections_kbs.choice_reg_callback.filter(), state='choice_device')
async def choice_device(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    tables = {'Хаб': 'SelectHub', 'Вторжение': 'SelectInvasion', 'Пожар': 'SelectFire', 'Протечка': 'SelectLeak',
              'Сирена': 'SelectSiren', 'Управление': 'SelectControl', 'ББП': 'SelectBBP'}
    data = await state.get_data()
    db.insert_choice_equipment(
        tables.get(data.get('table')),
        'id_tg, name',
        {'id_tg': call.from_user.id, 'name': callback_data.get('model')},
        {'id_tg': call.from_user.id}
    )
    await call.message.answer(f'Вы выбрали {callback_data.get("model")}', reply_markup=keyboards.menu)
    await state.finish()
