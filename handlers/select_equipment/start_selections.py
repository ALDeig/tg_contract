from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from misc import dp


class Selections(StatesGroup):
    q_1 = State()


@dp.message_handler(text='⚙️Подбор оборудования')
async def step_1(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup([
        [KeyboardButton(text='Камеры'), KeyboardButton(text='Регистраторы')],
        [KeyboardButton(text='Коммутаторы'), KeyboardButton(text='HDD'), KeyboardButton(text='Шкаф')],
        [KeyboardButton(text='Кабель'), KeyboardButton(text='Гофра'), KeyboardButton(text='ИБП')],
        [KeyboardButton(text='↩Отмена')]
    ], resize_keyboard=True)
    await message.answer('Выберите оборудование для подбора', reply_markup=keyboard)
    await Selections.q_1.set()


# @dp.message_handler(state=CameraSelections.q_1)
# async def selection_equipments(message: Message, state: FSMContext):
#