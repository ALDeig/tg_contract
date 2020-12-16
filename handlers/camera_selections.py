import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile, ReplyKeyboardRemove

import db
import keyboards
import inline_keybords
from misc import dp


class CameraSelections(StatesGroup):
    q_1 = State()
    q_2 = State()
    q_3 = State()
    q_4 = State()


@dp.message_handler(text='Подбор оборудования')
async def step_1(message: types.Message, state: FSMContext):
    await message.answer('Какой тип камеры подобрать?', reply_markup=keyboards.camera_selection_body)
    await CameraSelections.q_1.set()


@dp.message_handler(state=CameraSelections.q_1)
async def step_2(message: types.Message, state: FSMContext):
    if message.text == 'Купольная':
        await state.update_data(body='cup')
    elif message.text == 'Цилиндрическая':
        await state.update_data(body='cyl')
    else:
        await state.update_data(body='com')

    await message.answer('Уличная или внутреняя?', reply_markup=keyboards.camera_selection_execute)
    await CameraSelections.next()


@dp.message_handler(state=CameraSelections.q_2)
async def step_3(message: types.Message, state: FSMContext):
    if message.text == 'Уличная':
        await state.update_data(execute='o')
    else:
        await state.update_data(execute='r')
    await message.answer('Разрешение камеры?', reply_markup=keyboards.camera_selection_ppi)
    await CameraSelections.next()


# 'id', 'model', 'description', 'specifications', 'price', 'image'
@dp.message_handler(state=CameraSelections.q_3)
async def step_4(message: types.Message, state: FSMContext):
    if message.text == '2mp':
        await state.update_data(ppi='2')
    else:
        await state.update_data(ppi='4')
    data = await state.get_data()
    cameras = db.get_data_of_cameras(data['body'], data['execute'], data['ppi'], 'hiwatch')
    if not cameras:
        await message.answer('Таких камер нет', reply_markup=keyboards.menu)
        await state.finish()
        return
    await message.answer('Выберите камеру:', reply_markup=keyboards.key_cancel)
    for camera in cameras:
        keyboard = inline_keybords.create_keyboard(camera[1])
        photo = InputFile(os.path.join('commercial_proposal', 'images', camera[-1]))
        await message.answer_photo(
            photo=photo,
            caption=f'{camera[1]}\nЦена: {camera[4]}',
            reply_markup=keyboard)


@dp.callback_query_handler(inline_keybords.choice_cameras_callback.filter(make='show'), state=CameraSelections.q_3)
async def step_5(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=5)

    camera = db.get_price_of_camera(model=callback_data.get('model'))
    caption = f'{camera[0]}\n' \
              f'{camera[1]}\n' \
              f'{camera[2]}\n' \
              f'Цена: {camera[3]}'
    keyboard = inline_keybords.create_keyboard_2(callback_data.get('model'))
    await call.message.edit_caption(caption=caption, reply_markup=keyboard)


@dp.callback_query_handler(inline_keybords.choice_cameras_callback.filter(make='choice'), state=CameraSelections.q_3)
async def step_6(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=30)
    data = await state.get_data()
    db.insert_choice_camera(data['body'], callback_data.get('model'), call.from_user.id)
    await call.message.edit_reply_markup()
    await call.message.answer(f'Вы выбрали {callback_data.get("model")}', reply_markup=keyboards.menu)
    await state.finish()
