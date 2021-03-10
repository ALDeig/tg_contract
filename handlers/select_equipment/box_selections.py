import os

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile, Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.exceptions import BadRequest

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


keyboard_start = ReplyKeyboardMarkup([
    [KeyboardButton(text='Телекоммуникационный шкаф 19’’')],
    [KeyboardButton(text='Настенный щит')]
], resize_keyboard=True)


@dp.message_handler(text='Шкаф', state=Selections.q_1)
async def step_1(message: Message, state: FSMContext):
    # keyboard = create_keyboard_reg_and_switch('', 'DataBox')
    # if not keyboard:
    #     await message.answer('Нет вариантов')
    #     return
    # await state.update_data(options=keyboard[1])
    await message.answer('Выберите тип', reply_markup=keyboard_start)
    await BoxSelection.q_1.set()


@dp.message_handler(state=BoxSelection.q_1)
async def step_1(message: Message, state: FSMContext):
    type_box = 0 if message.text == 'Настенный щит' else 1
    keyboard = create_keyboard_reg_and_switch('brand', 'DataBox', {'type_box': type_box})
    if not keyboard:
        await message.answer('Нет вариантов')
        return
    await state.update_data({'options': keyboard[1], 'type_box': type_box})
    await message.answer('Выберите бренд', reply_markup=keyboard[0])
    await BoxSelection.q_2.set()


@dp.message_handler(state=BoxSelection.q_2)
async def step_2(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text not in data['options']:
        await message.answer('Выбери вариант')
        return
    if data.get('type_box') == 0:
        columns = 'id, model, price, image, specifications, description'
        data.pop('options')
        data['brand'] = message.text
        boxes = db.get_data_equipments('DataBox', columns, data)
        await message.answer('Выбери вариант')
        for box in boxes:
            keyboard = create_inline_keyboard(box[1])
            try:
                name = box[1].strip().replace('/', '').replace('\\', '')
                # type_file = box[3].split('.')[-1]
                photo = InputFile(os.path.join('commercial_proposal', 'images', 'box', data['brand'],
                                               name + '.jpg'))
                await message.answer_photo(
                    photo=photo,
                    caption=f'{box[1]}\nЦена: {box[2]}₽',
                    reply_markup=keyboard)
            except Exception as e:
                await message.answer(text=f'{box[1]}\nЦена: {box[2]}₽', reply_markup=keyboard)
        await BoxSelection.q_3.set()
        return
    await state.update_data(brand=message.text)
    keyboard = create_keyboard_reg_and_switch('number_units', 'DataBox', {'brand': message.text,
                                                                          'type_box': data['type_box']})
    await state.update_data(options=keyboard[1])
    await message.answer('Выбери количество юнитов', reply_markup=keyboard[0])
    await BoxSelection.q_3.set()


@dp.message_handler(state=BoxSelection.q_3)
async def step_3(message: Message, state: FSMContext):
    data = await state.get_data()
    if int(message.text) not in data['options']:
        await message.answer('Выбери вариант')
        return
    await state.update_data(number_units=message.text)
    data['number_units'] = message.text
    columns = 'id, model, price, image, specifications, description'
    data.pop('options')
    boxes = db.get_data_equipments('DataBox', columns, data)
    await message.answer('Выбери вариант')
    for box in boxes:
        keyboard = create_inline_keyboard(box[1])
        try:
            name = box[1].strip().replace('/', '').replace('\\', '')
            # type_file = box[3].split('.')[-1]
            photo = InputFile(os.path.join('commercial_proposal', 'images', 'box', data['brand'],
                                           name + '.jpg'))
            await message.answer_photo(
                photo=photo,
                caption=f'{box[1]}\nЦена: {box[2]}₽',
                reply_markup=keyboard)
        except Exception as e:
            await message.answer(text=f'{box[1]}\nЦена: {box[2]}₽', reply_markup=keyboard)


@dp.callback_query_handler(choice_reg_callback.filter(make='show'), state=BoxSelection.q_3)
async def step_6(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=5)
    recorder = db.get_equipment_data_by_model('DataBox', 'model, description, specifications, price',
                                              callback_data.get('model'))
    caption = f'{recorder[0]}\n' \
              f'{recorder[1]}\n' \
              f'{recorder[2]}\n' \
              f'Цена: {recorder[3]}₽'
    keyboard = create_inline_keyboard_2(callback_data.get('model'))
    try:
        await call.message.edit_caption(caption=caption, reply_markup=keyboard)
    except BadRequest:
        await call.message.edit_text(text=caption, reply_markup=keyboard)


@dp.callback_query_handler(choice_reg_callback.filter(make='choice'), state=BoxSelection.q_3)
async def step_5(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=10)
    data = await state.get_data()
    data.update({'id_tg': call.from_user.id, 'model': callback_data.get('model')})
    data.pop('options')
    try:
        data.pop('brand')
    except KeyError:
        pass
    columns = ', '.join(data.keys())
    # return
    db.insert_choice_equipment('ChoiceBox', columns, data, data)
    await call.message.edit_reply_markup()
    await call.message.answer(f'Вы выбрали {callback_data.get("model")}', reply_markup=keyboards.menu_video)
    await state.finish()
