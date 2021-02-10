from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile, Message, CallbackQuery

import db
from keyboards import keyboards
from keyboards.selection_equipments.other_select import create_keyboard_other
from misc import dp
from handlers.select_equipment.start_selections import Selections


class GofraSelection(StatesGroup):
    q_1 = State()
    q_2 = State()
    q_3 = State()
    q_4 = State()


@dp.message_handler(text='Гофра', state=Selections.q_1)
async def step_1(message: Message, state: FSMContext):
    keyboard = create_keyboard_other('brand', 'DataCable', {'type_cable': 'Гофра'})
    await state.update_data(options=keyboard[1])
    await message.answer('Выберите бренд', reply_markup=keyboard[0])
    await GofraSelection.q_1.set()


@dp.message_handler(state=GofraSelection.q_1)
async def step_2(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text not in data['options']:
        await message.answer('Выберите вариант')
        return
    data.update({'id_tg': message.from_user.id, 'brand': message.text})
    data.pop('options')
    columns = ', '.join(data.keys())
    db.insert_choice_equipment('ChoiceGofra', columns, data)
    await message.answer(f'Вы выбрали {message.text}', reply_markup=keyboards.menu_video)
    await state.finish()
