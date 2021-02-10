from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile, Message, CallbackQuery

import db
from keyboards import keyboards
from keyboards.selection_equipments.other_select import create_keyboard_other
from misc import dp
from handlers.select_equipment.start_selections import Selections


class CableSelection(StatesGroup):
    q_0 = State()
    q_1 = State()
    q_2 = State()
    q_3 = State()
    q_4 = State()

# Гофрированная труба
@dp.message_handler(text='Кабель', state=Selections.q_1)
async def step_1(message: Message, state: FSMContext):
    keyboard = create_keyboard_other('type_system', 'DataCable', {'type_cable': 'Кабель'})
    await state.update_data(options=keyboard[1])
    await message.answer('Выберите тип системы', reply_markup=keyboard[0])
    await CableSelection.q_0.set()


@dp.message_handler(state=CableSelection.q_0)
async def step_1(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text not in data['options']:
        await message.answer('Выбери вариант')
        return
    keyboard = create_keyboard_other('use', 'DataCable', {'type_system': message.text,'type_cable': 'Кабель'})
    await state.update_data(type_system=message.text)
    await state.update_data(options=keyboard[1])
    await message.answer('Выберите назначение', reply_markup=keyboard[0])
    await CableSelection.q_1.set()


@dp.message_handler(state=CableSelection.q_1)
async def step_2(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text not in data['options']:
        await message.answer('Выберите вариант')
        return
    keyboard = create_keyboard_other('brand', 'DataCable', {'type_system': data['type_system'],'type_cable': 'Кабель', 'use': message.text})
    await state.update_data(options=keyboard[1])
    await state.update_data(use=message.text)
    await message.answer('Выберите бренд', reply_markup=keyboard[0])
    await CableSelection.next()


@dp.message_handler(state=CableSelection.q_2)
async def step_3(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text not in data['options']:
        await message.answer('Выберите вариант')
        return
    data.update({'id_tg': message.from_user.id, 'brand': message.text})
    data.pop('options')
    columns = ', '.join(data.keys())
    db.insert_choice_equipment('ChoiceCable', columns, data)
    await message.answer(f'Вы выбрали {message.text}', reply_markup=keyboards.menu_video)
    await state.finish()