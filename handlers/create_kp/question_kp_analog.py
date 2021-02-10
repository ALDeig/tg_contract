# import os

# import asyncio
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, InputFile, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

# import analytics
# import db
from keyboards import keyboards
# from commercial_proposal import calculate_kp, create_doc
# from handlers.get_cost_of_work import DataPrices
from handlers.questions_of_kp import DataPoll
from misc import dp

class DataPollAnalog(StatesGroup):
    ip_system = State()
    total_numb_of_cam = State()  # total_cams
    indoor_cameras = State()  # cams_on_indoor
    cams_on_street = State()  # cams_on_street
    type_cams_in_room = State()  # type_cam_on_street
    type_cams_on_street = State()  # type_cam_in_room
    days_for_archive = State()  # days_for_archive
    answer_total_price = State()
    answer_of_sale = State()


@dp.message_handler(text='Аналоговая', state=DataPoll.system)
async def step_0(message: Message, state: FSMContext):
    key_cancel = ReplyKeyboardMarkup([
        [KeyboardButton(text='↩Отмена')]
    ], resize_keyboard=True)
    # await state.update_data(type_cam='IP')
    await message.answer('В разработке!', reply_markup=key_cancel)
    # await message.answer('Какое общее количество камер надо установить?', reply_markup=keyboards.key_cancel)
    # await DataPoll.next()


# @dp.message_handler(text='↩Отмена', state=DataPoll.system)
# async def step_1(message: Message, state: FSMContext):
#     await message.answer('Выбери действие', reply_markup=keyboards.menu_video)
#     await state.finish()