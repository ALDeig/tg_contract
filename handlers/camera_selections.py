import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile

import db
import keyboards
import inline_keybords
from misc import dp


class CameraSelections(StatesGroup):
    q_1 = State()
    q_2 = State()
    q_3 = State()
    q_4 = State()


@dp.message_handler(text='⚙️Подбор оборудования')
async def step_1(message: types.Message, state: FSMContext):
    keyboard = keyboards.create_keyboard_kp('brand')
    if not keyboard:
        await message.answer('Нет вариантов')
    await state.update_data(options=keyboard[1])
    await message.answer('Выберите бренд', reply_markup=keyboard[0])
    await CameraSelections.q_1.set()


@dp.message_handler(state=CameraSelections.q_1)
async def step_2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    options = data['options']
    if message.text not in options:
        await message.answer('Выберите вариант')
        return
    await state.update_data(brand=message.text)
    keyboard = keyboards.create_keyboard_kp('view_cam', {'brand': message.text})
    await state.update_data(options=keyboard[1])
    await message.answer('Какой тип камеры подобрать?', reply_markup=keyboard[0])
    await CameraSelections.q_2.set()


@dp.message_handler(state=CameraSelections.q_2)
async def step_3(message: types.Message, state: FSMContext):
    """Ловит ответ кнопки типа камеры."""
    data = await state.get_data()
    if message.text[2:] not in data['options']:
        await message.answer('Выебрите вариант')
        return
    await state.update_data(view_cam=message.text[2:])
    keyboard = keyboards.create_keyboard_kp('purpose', {'brand': data['brand'], 'view_cam': message.text[2:]})
    if not keyboard:
        await message.answer('Вариантов нет', reply_markup=keyboards.key_cancel)
        return
    await state.update_data(options=keyboard[1])
    await message.answer('Уличная или внутреняя?', reply_markup=keyboard[0])
    await CameraSelections.next()


@dp.message_handler(state=CameraSelections.q_3)
async def step_4(message: types.Message, state: FSMContext):
    """Ловит ответ кнопки о типе камеры, уличная или внутреняя"""
    data = await state.get_data()
    if message.text not in data['options']:
        await message.answer('Выберите вариант')
        return
    keyboard = keyboards.create_keyboard_kp('ppi', {'brand': data['brand'], 'view_cam': data['view_cam']})
    if not keyboard:
        await message.answer('Вариантов нет')
        return
    await state.update_data({'options': keyboard[1], 'purpose': message.text})
    await message.answer('Разрешение камеры?', reply_markup=keyboard[0])
    await CameraSelections.next()


@dp.message_handler(state=CameraSelections.q_4)
async def step_5(message: types.Message, state: FSMContext):
    """Ловит ответ кнопки разрешения камеры"""
    data = await state.get_data()
    if message.text not in data['options']:
        await message.answer('Выберите разрешение камеры')
        return
    data = await state.get_data()
    cameras = db.get_data_of_cameras(data['view_cam'], data['purpose'], message.text, data['brand'])
    if not cameras:
        await message.answer('Таких камер нет. Выберети другие параметры.')
        await message.answer('Выберите бренд', reply_markup=keyboards.create_keyboard_kp('brand'))
        await state.finish()
        await CameraSelections.q_1.set()
        return
    await message.answer('Выберите камеру:', reply_markup=keyboards.key_cancel)
    for camera in cameras:
        keyboard = inline_keybords.create_keyboard(camera[1])
        photo = InputFile(os.path.join('commercial_proposal', 'images', data['brand'], camera[1] + '.jpg'))
        await message.answer_photo(
            photo=photo,
            caption=f'{camera[1]}\nЦена: {camera[4]}₽',
            reply_markup=keyboard)


@dp.callback_query_handler(inline_keybords.choice_cameras_callback.filter(make='show'), state=CameraSelections.q_4)
async def step_6(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=5)
    camera = db.get_price_of_camera(model=callback_data.get('model'))
    caption = f'{camera[0]}\n' \
              f'{camera[1]}\n' \
              f'{camera[2]}\n' \
              f'Цена: {camera[3]}₽'
    keyboard = inline_keybords.create_keyboard_2(callback_data.get('model'))
    await call.message.edit_caption(caption=caption, reply_markup=keyboard)


@dp.callback_query_handler(inline_keybords.choice_cameras_callback.filter(make='choice'), state=CameraSelections.q_4)
async def step_7(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=30)
    data = await state.get_data()
    db.insert_choice_camera(data['view_cam'], data['purpose'], callback_data.get('model'), call.from_user.id)
    await call.message.edit_reply_markup()
    await call.message.answer(f'Вы выбрали {callback_data.get("model")}', reply_markup=keyboards.menu_video)
    await state.finish()
