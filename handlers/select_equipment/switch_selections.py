import os

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile, Message, CallbackQuery

import db
from keyboards import keyboards
from keyboards.selection_equipments.rec_selections_kbs import create_keyboard_reg_and_switch, create_inline_keyboard, \
    create_inline_keyboard_2, choice_reg_callback
from misc import dp
from handlers.select_equipment.start_selections import Selections


class SwitchSelection(StatesGroup):
    q_1 = State()
    q_2 = State()
    q_3 = State()
    q_4 = State()


@dp.message_handler(text='Коммутаторы', state=Selections.q_1)
async def step_1(message: Message, state: FSMContext):
    keyboard = create_keyboard_reg_and_switch('brand', 'DataSwitch')
    if not keyboard:
        await message.answer('Нет вариантов')
        return
    await state.update_data(options=keyboard[1])
    await message.answer('Выберите бренд', reply_markup=keyboard[0])
    await SwitchSelection.q_1.set()


@dp.message_handler(state=SwitchSelection.q_1)
async def step_2(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text not in data['options']:
        await message.answer('Выбери вариант')
        return
    await state.update_data(brand=message.text)
    keyboard = create_keyboard_reg_and_switch('ports_poe', 'DataSwitch', {'brand': message.text})
    await state.update_data(options=keyboard[1])
    await message.answer('Выбери количество портов', reply_markup=keyboard[0])
    await SwitchSelection.q_2.set()


@dp.message_handler(state=SwitchSelection.q_2)
async def step_3(message: Message, state: FSMContext):
    data = await state.get_data()
    if int(message.text) not in data['options']:
        await message.answer('Выбери вариант')
        return
    await state.update_data(ports_poe=message.text)
    data['ports_poe'] = message.text
    columns = 'id, model, price, image, specifications, description'
    data.pop('options')
    switches = db.get_data_equipments('DataSwitch', columns, data)
    await message.answer('Выбери вариант', reply_markup=keyboards.key_cancel_to_video)
    for switch in switches:
        keyboard = create_inline_keyboard(switch[1])
        try:
            name = switch[1].strip().replace('/', '').replace('\\', '')
            # type_file = switch[3].split('.')[-1]
            photo = InputFile(os.path.join('commercial_proposal', 'images', 'switch', data['brand'],
                                           name + '.jpg'))
            await message.answer_photo(
                photo=photo,
                caption=f'{switch[1]}\nЦена: {switch[2]}₽',
                reply_markup=keyboard)
        # except FileNotFoundError as e:
        #     print('Ошибка при отправке фото: ', e)
        #     await message.answer(text=f'{switch[1]}\nЦена: {switch[4]}₽', reply_markup=keyboard)
        except Exception as e:
            # print('Ошибка отправки сообщения: ', e)
            await message.answer(text=f'{switch[1]}\nЦена: {switch[4]}₽', reply_markup=keyboard)


@dp.callback_query_handler(choice_reg_callback.filter(make='show'), state=SwitchSelection.q_2)
async def step_6(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=5)
    recorder = db.get_equipment_data_by_model('DataSwitch', 'model, description, specifications, price',
                                              callback_data.get('model'))
    caption = f'{recorder[0]}\n' \
              f'{recorder[1]}\n' \
              f'{recorder[2]}\n' \
              f'Цена: {recorder[3]}₽'
    keyboard = create_inline_keyboard_2(callback_data.get('model'))
    await call.message.edit_caption(caption=caption, reply_markup=keyboard)


@dp.callback_query_handler(choice_reg_callback.filter(make='choice'), state=SwitchSelection.q_2)
async def step_5(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=10)
    data = await state.get_data()
    data.update({'id_tg': call.from_user.id, 'model': callback_data.get('model')})
    data.pop('options')
    data.pop('brand')
    columns = ', '.join(data.keys())
    # return
    db.insert_choice_equipment('ChoiceSwitch', columns, data)
    await call.message.edit_reply_markup()
    await call.message.answer(f'Вы выбрали {callback_data.get("model")}', reply_markup=keyboards.menu_video)
    await state.finish()
