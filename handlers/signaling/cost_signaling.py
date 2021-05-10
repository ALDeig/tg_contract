from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ContentTypes

import config
import db
from keyboards import keyboards
from misc import dp


@dp.message_handler(text='Ajax')
async def step_1(msg: Message, state: FSMContext):
    await msg.answer('Укажите стоимость монтажа и настройки Датчика движения')
    await state.set_state('cost_signaling')


@dp.message_handler(state='cost_signaling')
async def step_2(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(motion_sensor=msg.text)
        await msg.answer('Укажите стоимость монтажа и настройки Датчика открытия')
        await state.set_state('cost_signaling_step_3')
    else:
        await msg.answer('Введите стоимость')


@dp.message_handler(state='cost_signaling_step_3')
async def step_3(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(open_sensor=msg.text)
        await msg.answer(
            text='Укажите стоимость монтажа и настройки Датчика дыма',
            reply_markup=keyboards.key_cancel
        )
        await state.set_state('cost_signaling_step_4')
    else:
        await msg.answer('Введите стоимость')


@dp.message_handler(state='cost_signaling_step_4')
async def step_4(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(smoke_detector=msg.text)
        await msg.answer(
            text='Укажите стоимость монтажа и настройки Датчика протечки',
            reply_markup=keyboards.key_cancel
        )
        await state.set_state('cost_signaling_step_5')
    else:
        await msg.answer('Введите стоимость')


@dp.message_handler(state='cost_signaling_step_5')
async def step_5(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(leakage_sensor=msg.text)
        await msg.answer(
            text='Укажите стоимость монтажа и настройки Сирены',
            reply_markup=keyboards.key_cancel
        )
        await state.set_state('cost_signaling_step_6')
    else:
        await msg.answer('Введите стоимость')


@dp.message_handler(state='cost_signaling_step_6')
async def step_6(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(siren=msg.text)
        await msg.answer('Укажите стоимость монтажа и настройки Клавиатуры управления',
                         reply_markup=keyboards.key_cancel)
        await state.set_state('cost_signaling_step_7')
    else:
        await msg.answer('Введите стоимость')


@dp.message_handler(state='cost_signaling_step_7')
async def step_7(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(control_keyboard=msg.text)
        await msg.answer(
            text='Укажите стоимость монтажа  и настройки Умной розетки',
            reply_markup=keyboards.key_cancel
        )
        await state.set_state('cost_signaling_step_8')
    else:
        await msg.answer('Введите стоимость')


@dp.message_handler(state='cost_signaling_step_8')
async def step_8(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(smart_plug=msg.text)
        await msg.answer(
            text='Укажите стоимость монтажа  и настройки Силового реле',
            reply_markup=keyboards.key_cancel
        )
        await state.set_state('cost_signaling_step_9')
    else:
        await msg.answer('Введите стоимость')


@dp.message_handler(state='cost_signaling_step_9')
async def step_9(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(power_relay=msg.text)
        await msg.answer(
            text='Укажите стоимость монтажа  и настройки Слаботочного реле',
            reply_markup=keyboards.key_cancel
        )
        await state.set_state('cost_signaling_step_10')
    else:
        await msg.answer('Введите стоимость')


@dp.message_handler(state='cost_signaling_step_10')
async def step_10(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data({
            'low_current_relay': msg.text,
            'id_tg': msg.from_user.id
        })
        data = await state.get_data()
        columns = tuple(data.keys())
        db.insert('cost_signaling', columns, data)
        await msg.answer('Выберите действие', reply_markup=keyboards.menu)
        await state.finish()
    else:
        await msg.answer('Введите стоимость')


