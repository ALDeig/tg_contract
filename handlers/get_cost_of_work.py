from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

import db
from misc import dp
import keyboards


class DataPrices(StatesGroup):
    installation_cost_of_1_IP_camera = State()  # стоимость монтажа 1 IP камеры, без прокладки кабеля
    installation_cost_of_1_meter = State()  # стоимость монтажа 1 метра кабеля в гофрированной трубе
    meters_of_cable = State()  # сколько метров кабеля в среднем надо учитывать в КП на 1 IP камеру
    cost_of_mount_kit = State()  # стоимость монтажного комплекта (стяжки, коннектора, изолента, клипсы) для 1 IP камеры
    start_up_cost = State()  # стоимость пуско-наладочных работ


@dp.message_handler(text='⚒ Изменить стоимость работ', state='*')
async def start_change_cost(message: types.Message):
    await message.answer(text='Укажите стоимость монтажа 1 IP камеры, без прокладки кабеля',
                         reply_markup=keyboards.key_cancel)
    await DataPrices.first()


@dp.message_handler(state=DataPrices.installation_cost_of_1_IP_camera)
async def step_1(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(text='Вы не верно указали количество')
        return
    await state.update_data(installation_1_cam=message.text)
    await message.answer(text='Укажите стоимость монтажа 1 метра кабеля в гофрированной трубе')
    await DataPrices.next()


@dp.message_handler(state=DataPrices.installation_cost_of_1_meter)
async def step_2(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(text='Вы не верно указали количество')
        return
    await state.update_data(installation_cable=message.text)
    await message.answer('Укажите сколько метров кабеля в среднем надо учитывать в КП на 1 IP камеру')
    await DataPrices.next()


@dp.message_handler(state=DataPrices.meters_of_cable)
async def step_3(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Вы не верно указали количество')
        return
    await state.update_data(meters_cable=message.text)
    await message.answer('Укажите стоимость монтажного комплекта (стяжки, коннектора, изолента, клипсы) для 1 IP '
                         'камеры')
    await DataPrices.next()


@dp.message_handler(state=DataPrices.cost_of_mount_kit)
async def step_4(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Вы не верно указали количество')
        return
    await state.update_data(cost_mount_kit=message.text)
    await message.answer('Укажите стоимость пуско-наладочных работ(настройка параметров камеры и записи на '
                         'регистраторе, юстировка) 1 IP камеры')
    await DataPrices.next()


@dp.message_handler(state=DataPrices.start_up_cost)
async def step_5(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Вы не верно указали стоимость')
        return
    await state.update_data(start_up_cost=message.text)
    await message.answer('Отлично, я сохранил эти данные и их не надо вводить каждый раз при создании КП, но есть '
                         'возможность их изменить в любой момент', reply_markup=keyboards.menu)
    data = await state.get_data()
    db.delete_cost_work(message.from_user.id)
    db.insert_cost(data, message.from_user.id)
    await state.finish()
