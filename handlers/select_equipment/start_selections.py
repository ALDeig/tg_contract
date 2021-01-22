from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from misc import dp


class Selections(StatesGroup):
    q_1 = State()


@dp.message_handler(text='⚙️Подбор оборудования')
async def step_1(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup([
        [KeyboardButton(text='Камера'), KeyboardButton(text='Регистратор')],
        [KeyboardButton(text='Коммутатор'), KeyboardButton(text='HDD'), KeyboardButton(text='Ящик')]
    ], resize_keyboard=True)
    await message.answer('Выберите оборудование для подбора', reply_markup=keyboard)
    await Selections.q_1.set()


# @dp.message_handler(state=CameraSelections.q_1)
# async def selection_equipments(message: Message, state: FSMContext):
#