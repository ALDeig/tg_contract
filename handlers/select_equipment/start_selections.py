from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

import db
from misc import dp
from keyboards import keyboards


class Selections(StatesGroup):
    q_1 = State()


@dp.message_handler(text='⚙️Подбор оборудования')
async def step_1(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup([
        [KeyboardButton(text='Камеры'), KeyboardButton(text='Регистраторы')],
        [KeyboardButton(text='Коммутаторы'), KeyboardButton(text='HDD'), KeyboardButton(text='Шкаф')],
        [KeyboardButton(text='Кабель'), KeyboardButton(text='Гофра'), KeyboardButton(text='ИБП')],
        [KeyboardButton(text='Установить оборудование по умолчанию')],
        [KeyboardButton(text='↩Отмена')]
    ], resize_keyboard=True)
    await message.answer('Выберите оборудование для подбора', reply_markup=keyboard)
    await Selections.q_1.set()


@dp.message_handler(text='Установить оборудование по умолчанию', state=Selections.q_1)
async def set_default_select(message: Message, state: FSMContext):
    db.set_default_select(message.from_user.id)
    await state.finish()
    await message.answer("Выберите действие", reply_markup=keyboards.menu_video)
# @dp.message_handler(state=CameraSelections.q_1)
# async def selection_equipments(message: Message, state: FSMContext):
#