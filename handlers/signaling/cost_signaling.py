from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ContentTypes

import config
import db
from keyboards import keyboards
from misc import dp


@dp.message_handler(text='Охранная сигнализация', state='type_system')
async def step_1(msg: Message, state: FSMContext):
    columns = 'hub, motion_sensor, open_sensor, smoke_detector, leakage_sensor, siren, control_keyboard, smart_plug, \
    power_relay, low_current_relay'
    old_cost = db.get_data(columns, 'cost_signaling', {'id_tg': ('=', str(msg.from_user.id))})
    if old_cost:
        old_cost = old_cost[0]
        await msg.answer(
            text=f'<b>Текущие данные:</b>\n\n'
                 f'Стоимость монтажа и настройки Датчика движения: {old_cost.motion_sensor}\n'
                 f'Стоимость монтажа и настройки Датчика открытия: {old_cost.open_sensor}\n'
                 f'Стоимость монтажа и настройки Датчика дыма: {old_cost.smoke_detector}\n'
                 f'Стоимость монтажа и настройки Датчика протечки: {old_cost.leakage_sensor}\n'
                 f'Стоимость монтажа и настройки Сирены: {old_cost.siren}\n'
                 f'Стоимость монтажа и настройки Клавиатуры управления: {old_cost.control_keyboard}\n'
                 f'Стоимость монтажа и настройки Умной розетки: {old_cost.smart_plug}\n'
                 f'Стоимость монтажа и настройки Силового реле: {old_cost.power_relay}\n'
                 f'Стоимость монтажа и настройки Слаботочного реле: {old_cost.low_current_relay}\n'
                 f'Стоимость монтажа и настройки Хаба: {old_cost.hub}\n',
            parse_mode='HTML'
        )
    await msg.answer(
        text='Укажите стоимость монтажа элементов охранной сигнализации (пока только оборудование Ajax)',
        reply_markup=keyboards.key_cancel)
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
        await msg.answer(text='Укажите стоимость монтажа и настройки Датчика дыма')
        await state.set_state('cost_signaling_step_4')
    else:
        await msg.answer('Введите стоимость')


@dp.message_handler(state='cost_signaling_step_4')
async def step_4(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(smoke_detector=msg.text)
        await msg.answer(text='Укажите стоимость монтажа и настройки Датчика протечки')
        await state.set_state('cost_signaling_step_5')
    else:
        await msg.answer('Введите стоимость')


@dp.message_handler(state='cost_signaling_step_5')
async def step_5(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(leakage_sensor=msg.text)
        await msg.answer(text='Укажите стоимость монтажа и настройки Сирены')
        await state.set_state('cost_signaling_step_6')
    else:
        await msg.answer('Введите стоимость')


@dp.message_handler(state='cost_signaling_step_6')
async def step_6(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(siren=msg.text)
        await msg.answer('Укажите стоимость монтажа и настройки Клавиатуры управления')
        await state.set_state('cost_signaling_step_7')
    else:
        await msg.answer('Введите стоимость')


@dp.message_handler(state='cost_signaling_step_7')
async def step_7(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(control_keyboard=msg.text)
        await msg.answer(text='Укажите стоимость монтажа  и настройки Умной розетки')
        await state.set_state('cost_signaling_step_8')
    else:
        await msg.answer('Введите стоимость')


@dp.message_handler(state='cost_signaling_step_8')
async def step_8(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(smart_plug=msg.text)
        await msg.answer(
            text='Укажите стоимость монтажа  и настройки Силового реле')
        await state.set_state('cost_signaling_step_9')
    else:
        await msg.answer('Введите стоимость')


@dp.message_handler(state='cost_signaling_step_9')
async def step_9(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(power_relay=msg.text)
        await msg.answer(
            text='Укажите стоимость монтажа  и настройки Слаботочного реле')
        await state.set_state('cost_signaling_step_10')
    else:
        await msg.answer('Введите стоимость')


@dp.message_handler(state='cost_signaling_step_10')
async def step_9(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(low_current_relay=msg.text)
        await msg.answer(
            text='Укажите стоимость монтажа  и настройки Хаба')
        await state.set_state('cost_signaling_step_11')
    else:
        await msg.answer('Введите стоимость')


@dp.message_handler(state='cost_signaling_step_11')
async def step_10(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data({
            'hub': msg.text,
            'id_tg': msg.from_user.id
        })
        data = await state.get_data()
        columns = tuple(data.keys())
        db.insert('cost_signaling', columns, data)
        await msg.answer('Я сохранил стоимость работ и буду учитывать её при создании всех КП.\n\nПоменять стоимость '
                         'работ можно в меню: 🎛 <b>Изменить данные</b>', parse_mode='HTML')
        await msg.answer('Выберите действие', reply_markup=keyboards.menu)
        await state.finish()
    else:
        await msg.answer('Введите стоимость')


