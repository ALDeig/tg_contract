import os

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile, Message, CallbackQuery

import db
from keyboards import keyboards
from keyboards.selection_equipments.rec_selections_kbs import create_keyboard_reg_and_switch, create_inline_keyboard, \
    create_inline_keyboard_2, choice_reg_callback
from misc import dp
from handlers.select_equipment.start_selections import Selections


class BoxSelection(StatesGroup):
    q_1 = State()
    q_2 = State()
    q_3 = State()
    q_4 = State()


@dp.message_handler(text='ТШ', state=Selections.q_1)
async def step_1(message: Message, state: FSMContext):
    keyboard = create_keyboard_reg_and_switch('brand', 'DataBox')
    if not keyboard:
        await message.answer('Нет вариантов')
        return
    await state.update_data(options=keyboard[1])
    await message.answer('Выберите бренд', reply_markup=keyboard[0])
    await BoxSelection.q_1.set()


@dp.message_handler(state=BoxSelection.q_1)
async def step_2(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text not in data['options']:
        await message.answer('Выбери вариант')
        return
    await state.update_data(brand=message.text)
    keyboard = create_keyboard_reg_and_switch('number_units', 'DataBox', {'brand': message.text})
    await state.update_data(options=keyboard[1])
    await message.answer('Выбери количество юнитов', reply_markup=keyboard[0])
    await BoxSelection.q_2.set()


@dp.message_handler(state=BoxSelection.q_2)
async def step_3(message: Message, state: FSMContext):
    data = await state.get_data()
    if int(message.text) not in data['options']:
        await message.answer('Выбери вариант')
        return
    await state.update_data(number_units=message.text)
    data['number_units'] = message.text
    columns = 'id, model, price, trade_price, specifications, description'
    data.pop('options')
    boxes = db.get_data_equipments('DataBox', columns, data)
    await message.answer('Выбери вариант')
    for box in boxes:
        keyboard = create_inline_keyboard(box[1])
        try:
            photo = InputFile(os.path.join('commercial_proposal', 'images', 'box', data['brand'],
                                           box[1].replace('/', '') + '.jpg'))
        except Exception as e:
            print(e)
            continue
        await message.answer_photo(
            photo=photo,
            caption=f'{box[1]}\nЦена: {box[2]}₽, Оптовая цена: {box[3]}₽',
            reply_markup=keyboard)


@dp.callback_query_handler(choice_reg_callback.filter(make='show'), state=BoxSelection.q_2)
async def step_6(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=5)
    recorder = db.get_equipment_data_by_model('DataBox', 'model, description, specifications, price',
                                              callback_data.get('model'))
    caption = f'{recorder[0]}\n' \
              f'{recorder[1]}\n' \
              f'{recorder[2]}\n' \
              f'Цена: {recorder[3]}₽'
    keyboard = create_inline_keyboard_2(callback_data.get('model'))
    await call.message.edit_caption(caption=caption, reply_markup=keyboard)


@dp.callback_query_handler(choice_reg_callback.filter(make='choice'), state=BoxSelection.q_2)
async def step_5(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=10)
    data = await state.get_data()
    data.update({'id_tg': call.from_user.id, 'model': callback_data.get('model')})
    data.pop('options')
    data.pop('brand')
    columns = ', '.join(data.keys())
    print(columns)
    print(data.values())
    # return
    db.insert_choice_equipment('ChoiceBox', columns, data)
    await call.message.edit_reply_markup()
    await call.message.answer(f'Вы выбрали {callback_data.get("model")}', reply_markup=keyboards.menu_video)
    await state.finish()
