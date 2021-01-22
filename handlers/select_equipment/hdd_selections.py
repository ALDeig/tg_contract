from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile, Message, CallbackQuery

import db
from keyboards import keyboards
from keyboards.selection_equipments.hdd_select_keyboard import create_keyboard_hdd
from misc import dp
from handlers.select_equipment.start_selections import Selections


class HDDSelections(StatesGroup):
    q_1 = State()
    q_2 = State()
    q_3 = State()


@dp.message_handler(text='HDD', state=Selections.q_1)
async def step_1(message: Message, state: FSMContext):
    keyboard = create_keyboard_hdd()
    await state.update_data(options=keyboard[1])
    await message.answer('Выберите бренд', reply_markup=keyboard[0])
    await HDDSelections.q_1.set()


@dp.message_handler(state=HDDSelections.q_1)
async def step_2(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text not in data['options']:
        await message.answer('Выберите вариант')
        return
    # await state.update_data({'id_tg': message.from_user.id, 'brand': message.text})
    data.update({'id_tg': message.from_user.id, 'brand': message.text})
    data.pop('options')
    columns = ', '.join(data.keys())
    db.insert_choice_equipment('ChoiceHDD', columns, data)
    await message.answer(f'Вы выбрали {message.text}', reply_markup=keyboards.menu_video)
    await state.finish()