import os

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile, Message, CallbackQuery
from aiogram.utils.exceptions import BadRequest

import db
from keyboards import keyboards, inline_keybords
from misc import dp
from handlers.select_equipment.start_selections import Selections


class CameraSelections(StatesGroup):
    q_0_0 = State()
    q_0 = State()
    q_1 = State()
    q_2 = State()
    q_3 = State()
    q_4 = State()


@dp.message_handler(text='Камеры', state=Selections.q_1)
async def step_1_0(message: Message, state: FSMContext):
    # keyboard = keyboards.create_keyboard_kp('type_cam', 'data_cameras')
    keyboard = keyboards.camera_selection_type
    # if not keyboard:
    #     await message.answer('Нет вариантов')
    # await state.update_data(options=keyboard[1])
    await message.answer('Выберите тип камеры', reply_markup=keyboard)
    await CameraSelections.q_0_0.set()


@dp.message_handler(state=CameraSelections.q_0_0)
async def step_1(message: Message, state: FSMContext):
    if message.text == 'IP':
        await state.update_data(type_cam=message.text)
        keyboard = keyboards.create_keyboard_kp('brand', 'data_cameras', {'type_cam': message.text})
        if not keyboard:
            await message.answer('Нет вариантов')
        await state.update_data(options=keyboard[1])
        await message.answer('Выберите бренд', reply_markup=keyboard[0])
        await CameraSelections.q_1.set()
    elif message.text == 'Аналоговые':
        await message.answer('В разработке', reply_markup=keyboards.key_cancel_to_video)
        return
        keyboard = keyboards.create_keyboard_kp('type_cam', 'data_cameras', ip_cam=False)
        if not keyboard:
            await message.answer('Нет вариантов')
        await state.update_data(options=keyboard[1])
        await message.answer('Выберите тип камеры', reply_markup=keyboard[0])
        await CameraSelections.q_0.set()
    else:
        await message.answer('Выберите вариант')

    # keyboard = keyboards.create_keyboard_kp('type_cam', 'data_cameras')
    # if not keyboard:
    #     await message.answer('Нет вариантов')
    # await state.update_data(options=keyboard[1])
    # await message.answer('Выберите тип камеры', reply_markup=keyboard[0])
    # await CameraSelections.q_0.set()


@dp.message_handler(state=CameraSelections.q_0)
async def step_1(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text not in data['options']:
        await message.answer('Выберите вариант')
        return
    await state.update_data(type_cam=message.text)
    keyboard = keyboards.create_keyboard_kp('brand', 'data_cameras', {'type_cam': message.text})
    if not keyboard:
        await message.answer('Нет вариантов')
    await state.update_data(options=keyboard[1])
    await message.answer('Выберите бренд', reply_markup=keyboard[0])
    await CameraSelections.q_1.set()


@dp.message_handler(state=CameraSelections.q_1)
async def step_2(message: Message, state: FSMContext):
    data = await state.get_data()
    options = data['options']
    if message.text not in options:
        await message.answer('Выберите вариант')
        return
    await state.update_data(brand=message.text)
    keyboard = keyboards.create_keyboard_kp('view_cam', 'data_cameras',
                                            {'type_cam': data['type_cam'], 'brand': message.text})
    await state.update_data(options=keyboard[1])
    await message.answer('Какой тип камеры подобрать?', reply_markup=keyboard[0])
    await CameraSelections.q_2.set()


@dp.message_handler(state=CameraSelections.q_2)
async def step_3(message: Message, state: FSMContext):
    """Ловит ответ кнопки типа камеры."""
    data = await state.get_data()
    if message.text[2:] not in data['options']:
        await message.answer('Выебрите вариант')
        return
    await state.update_data(view_cam=message.text[2:])
    keyboard = keyboards.create_keyboard_kp('purpose', 'data_cameras',
                                            {'type_cam': data['type_cam'], 'brand': data['brand'],
                                             'view_cam': message.text[2:]})
    if not keyboard:
        await message.answer('Вариантов нет', reply_markup=keyboards.key_cancel_to_video)
        return
    await state.update_data(options=keyboard[1])
    await message.answer('Уличная или внутреняя?', reply_markup=keyboard[0])
    await CameraSelections.next()


@dp.message_handler(state=CameraSelections.q_3)
async def step_4(message: Message, state: FSMContext):
    """Ловит ответ кнопки о типе камеры, уличная или внутреняя"""
    data = await state.get_data()
    if message.text not in data['options']:
        await message.answer('Выберите вариант')
        return
    keyboard = keyboards.create_keyboard_kp('ppi', 'data_cameras',
                                            {'type_cam': data['type_cam'], 'brand': data['brand'],
                                             'view_cam': data['view_cam']})
    if not keyboard:
        await message.answer('Вариантов нет')
        return
    await state.update_data({'options': keyboard[1], 'purpose': message.text})
    await message.answer('Разрешение камеры в Мп.?', reply_markup=keyboard[0])
    await CameraSelections.next()


@dp.message_handler(text='Да', state=CameraSelections.q_4)
async def step_pagin(message: Message, state: FSMContext):
    data = await state.get_data()
    end = data['end'] + 5
    start = data['start'] + 5
    cameras = data['cameras']
    for camera in cameras[start:end]:
        keyboard = inline_keybords.create_keyboard(camera[1])
        try:
            name = camera[1].strip().replace('/', '').replace('\\', '')
            # type_file = camera[-1].split('.')[-1]
            photo = InputFile(os.path.join('commercial_proposal', 'images', 'camera', data['brand'],
                                           name + '.jpg'))
            await message.answer_photo(
                photo=photo,
                caption=f'{camera[1]}\nЦена: {camera[4]}₽',
                reply_markup=keyboard)
        except FileNotFoundError as e:
            print('Ошибка при отправке фото: ', e)
            await message.answer(text=f'{camera[1]}\nЦена: {camera[4]}₽', reply_markup=keyboard)
        except Exception as e:
            print('Ошибка отправки сообщения: ', e)
            continue
    if end < len(cameras):
        await state.update_data({'end': end, 'start': start})
        await message.answer('Показать еще?', reply_markup=keyboards.yes)
    else:
        await message.answer('Это все варианты', reply_markup=keyboards.key_cancel_to_video)


@dp.message_handler(state=CameraSelections.q_4)
async def step_5(message: Message, state: FSMContext):
    """Ловит ответ кнопки разрешения камеры"""
    data = await state.get_data()
    if message.text not in data['options']:
        await message.answer('Выберите разрешение камеры')
        return
    cameras = db.get_data_of_cameras(data['type_cam'], data['view_cam'], data['purpose'], message.text, data['brand'])
    if not cameras:
        await message.answer('Таких камер нет. Выберети другие параметры.')
        await message.answer('Выберите тип камеры',
                             reply_markup=keyboards.camera_selection_type)
        await state.finish()
        await CameraSelections.q_0_0.set()
        return
    await message.answer('Выберите камеру:', reply_markup=keyboards.key_cancel_to_video)
    await state.update_data(cameras=cameras)
    end = 5
    for camera in cameras[:end]:
        keyboard = inline_keybords.create_keyboard(camera[1])
        try:
            name = camera[1].strip().replace('/', '').replace('\\', '')
            type_file = camera[-1].split('.')[-1]
            photo = InputFile(os.path.join('commercial_proposal', 'images', 'camera', data['brand'],
                                           name + f'.{type_file}'))
            await message.answer_photo(
                photo=photo,
                caption=f'{camera[1]}\nЦена: {camera[4]}₽',
                reply_markup=keyboard)
        except FileNotFoundError as e:
            print('Ошибка при отправке фото: ', e)
            await message.answer(text=f'{camera[1]}\nЦена: {camera[4]}₽', reply_markup=keyboard)
        except Exception as e:
            print('Ошибка отправки сообщения: ', e)
            continue
    if end < len(cameras):
        await state.update_data({'start': 0, 'end': end})
        keyboard = keyboards.yes
        await message.answer(text='Показать еще', reply_markup=keyboard)
    else:
        await message.answer('Это все варианты')

#
# @dp.message_handler(text='Да', state=CameraSelections.q_4)
# async def step_pagin(message: Message, state: FSMContext):
#     data = await state.get_data()
#     end = data['end'] + 5
#     start = data['start'] + 5
#     cameras = data['cameras']
#     for camera in cameras[start:end]:
#         keyboard = inline_keybords.create_keyboard(camera[1])
#         try:
#             photo = InputFile(os.path.join('commercial_proposal', 'images', 'camera', data['brand'],
#                                            camera[1].replace('/', '') + '.jpg'))
#             await message.answer_photo(
#                 photo=photo,
#                 caption=f'{camera[1]}\nЦена: {camera[4]}₽',
#                 reply_markup=keyboard)
#         except FileNotFoundError as e:
#             print('Ошибка при отправке фото: ', e)
#             await message.answer(text=f'{camera[1]}\nЦена: {camera[4]}₽', reply_markup=keyboard)
#         except Exception as e:
#             print('Ошибка отправки сообщения: ', e)
#             continue
#     if end < len(cameras):
#         await state.update_data({'end': end, 'start': start})
#         await message.answer('Показать еще?', reply_markup=keyboards.yes)
#     else:
#         await message.answer('Это все варианты', reply_markup=keyboards.key_cancel_to_video)


@dp.callback_query_handler(inline_keybords.choice_cameras_callback.filter(make='show'), state=CameraSelections.q_4)
async def step_6(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=5)
    camera = db.get_price_of_camera(model=callback_data.get('model'))
    print(camera)
    caption = f'{camera[0]}\n' \
              f'{camera[1]}\n' \
              f'{camera[2][:900]}\n' \
              f'Цена: {camera[3]}₽'
    keyboard = inline_keybords.create_keyboard_2(callback_data.get('model'))
    print(callback_data.get('model'))
    # await call.messExceptioage.edit_caption(caption=caption, reply_markup=keyboard)
    # print(call.message)
    # await call.message.edit_caption(caption=caption, reply_markup=keyboard)
    try:
        # print('photo')
        await call.message.edit_caption(caption=caption, reply_markup=keyboard)
    except BadRequest:
        print('message')
        await call.message.edit_text(text=caption, reply_markup=keyboard)


@dp.callback_query_handler(inline_keybords.choice_cameras_callback.filter(make='choice'), state=CameraSelections.q_4)
async def step_7(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=30)
    data = await state.get_data()
    db.insert_choice_camera(data['view_cam'], data['purpose'], callback_data.get('model'), call.from_user.id)
    await call.message.edit_reply_markup()
    await call.message.answer(f'Вы выбрали {callback_data.get("model")}', reply_markup=keyboards.menu_video)
    await state.finish()
