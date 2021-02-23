import os

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile, Message, CallbackQuery
from aiogram.utils.exceptions import BadRequest
from loguru import logger

import db
from keyboards import keyboards
from keyboards.selection_equipments.rec_selections_kbs import create_keyboard_reg_and_switch, create_inline_keyboard, \
    create_inline_keyboard_2, choice_reg_callback
from misc import dp
from handlers.select_equipment.start_selections import Selections


class RegSelections(StatesGroup):
    q_1 = State()
    q_2 = State()
    q_2_1 = State()
    q_3 = State()
    q_4 = State()


@dp.message_handler(text='Регистраторы', state=Selections.q_1)
async def step_1(message: Message, state: FSMContext):
    keyboard = create_keyboard_reg_and_switch('type_recorder', 'DataRecorder')
    if not keyboard:
        await message.answer('Нет вариантов')
        return
    await state.update_data(options=keyboard[1])
    await message.answer('Выберите тип системы', reply_markup=keyboard[0])
    await RegSelections.q_1.set()


@dp.message_handler(state=RegSelections.q_1)
async def step_2(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text not in data['options']:
        await message.answer('Выберите вариант из списка')
        return
    # if message.text != 'Сетевые (IP)':
    #     await message.answer('В разработке', reply_markup=keyboards.key_cancel_to_video)
    #     return
    await state.update_data(type_recorder=message.text)
    keyboard = create_keyboard_reg_and_switch('brand', 'DataRecorder', {'type_recorder': message.text})
    await state.update_data(options=keyboard[1])
    await message.answer('Выберите бренд', reply_markup=keyboard[0])
    await RegSelections.q_2.set()


@dp.message_handler(state=RegSelections.q_2)
async def step_3_1(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text not in data['options']:
        await message.answer('Выбери вариант')
        return
    await state.update_data(brand=message.text)
    filters = {'type_recorder': data['type_recorder'], 'brand': message.text}
    keyboard = create_keyboard_reg_and_switch('number_channels', 'DataRecorder', filters)
    await state.update_data(options=keyboard[1])
    await message.answer('Какое количество каналов?', reply_markup=keyboard[0])
    await RegSelections.q_2_1.set()


@dp.message_handler(state=RegSelections.q_2_1)
async def step_3(message: Message, state: FSMContext):
    data = await state.get_data()
    if int(message.text) not in data['options']:
        await message.answer('Выберите вариант')
        return
    await state.update_data(number_channels=message.text)
    filters = {'type_recorder': data['type_recorder'], 'brand': data['brand'], 'number_channels': message.text}
    keyboard = create_keyboard_reg_and_switch('number_hdd', 'DataRecorder', filters)
    await state.update_data(options=keyboard[1])
    await message.answer('Какое количество дисков?', reply_markup=keyboard[0])
    await RegSelections.q_3.set()


# @dp.message_handler(state=RegSelections.q_2_1)
# async def step_3_1(message: Message, state: FSMContext):
#     data = await state.get_data()
#     if message.text not in data['options']:
#         await message.answer('Выбери вариант')
#         return
#     await state.update_data(number_hdd=message.text)
#     filters = {'type_recorder': data['type_recorder'], 'brand': data['brand'], 'number_hdd': message.text}
#     keyboard = create_keyboard_reg_and_switch('number_channels', 'DataRecorder', filters)
#     await state.update_data(options=keyboard[1])
#     await message.answer('Какое количество каналов?', reply_markup=keyboard[0])
#     await RegSelections.q_3.set()


# @dp.message_handler(state=RegSelections.q_3)
# async def step_4(message: Message, state: FSMContext):
#     data = await state.get_data()
#     if int(message.text) not in data['options']:
#         await message.answer('Выберите вариант')
#         return
#     await state.update_data(number_hdd=message.text)
#     filters = {'type_recorder': data['type_recorder'], 'brand': data['brand'], 'number_hdd': message.text}
#     keyboard = create_keyboard_reg_and_switch('number_poe', 'DataRecorder', filters)
#     await state.update_data(options=keyboard[1])
#     await message.answer('Какое количество PoE портов?', reply_markup=keyboard[0])
#     await RegSelections.q_4.set()


# @dp.message_handler(text='Да', state=RegSelections.q_3)
# async def step_pagin(message: Message, state: FSMContext):
#     data = await state.get_data()
#     end = data['end'] + 5
#     start = data['start'] + 5
#     cameras = data['cameras']
#     for camera in cameras[start:end]:
#         keyboard = inline_keybords.create_keyboard(camera[1])
#         try:
#             name = camera[1].strip().replace('/', '').replace('\\', '')
#             type_file = camera[-1].split('.')[-1]
#             photo = InputFile(os.path.join('commercial_proposal', 'images', 'camera', data['brand'],
#                                            name + f'.{type_file}'))
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


@dp.message_handler(state=RegSelections.q_3)
async def step_4(message: Message, state: FSMContext):
    data = await state.get_data()
    if int(message.text) not in data['options']:
        await message.answer('Выберите вариант')
        return
    await state.update_data(number_hdd=message.text)
    data['number_hdd'] = message.text
    # data['number_poe'] = message.text
    columns = 'id, model, price, image, specifications, description'
    data.pop('options')
    recorders = db.get_data_equipments('DataRecorder', columns, data)
    await message.answer('Выберите вариант', reply_markup=keyboards.key_cancel_to_video)
    for recorder in recorders:
        keyboard = create_inline_keyboard(recorder[1])
        try:
            name = recorder[1].strip().replace('/', '').replace('\\', '')
            # type_file = recorder[3].split('.')[-1]
            photo = InputFile(os.path.join('commercial_proposal', 'images', 'recorder', data['brand'],
                                           name + '.jpg'))
            await message.answer_photo(
                photo=photo,
                caption=f'{recorder[1]}\nЦена: {recorder[2]}',
                reply_markup=keyboard)
        except FileNotFoundError as e:
            await message.answer(text=f'{recorder[1]}\nЦена: {recorder[2]}', reply_markup=keyboard)
        except Exception as e:
            print(e)
            await message.answer(text=f'{recorder[1]}\nЦена: {recorder[2]}', reply_markup=keyboard)
    # filters = {'type_recorder': data['type_recorder'], 'brand': data['brand'], 'number_hdd': message.text}
    # keyboard = create_keyboard_reg_and_switch('number_poe', 'DataRecorder', filters)
    # await state.update_data(options=keyboard[1])
    # await message.answer('Какое количество PoE портов?', reply_markup=keyboard[0])
    # await RegSelections.q_4.set()

# @dp.message_handler(state=RegSelections.q_4)
# async def step_5(message: Message, state: FSMContext):
#     data = await state.get_data()
#     if int(message.text) not in data['options']:
#         print(data['options'])
#         await message.answer('Выберите вариант')
#         return
#     await state.update_data(number_poe=message.text)
#     data['number_poe'] = message.text
#     columns = 'id, model, price, trade_price, specifications, description'
#     data.pop('options')
#     recorders = db.get_data_equipments('DataRecorder', columns, data)
#     print(recorders, 'no recorders')
#     await message.answer('Выберите вариант', reply_markup=keyboards.key_cancel)
#     for recorder in recorders:
#         keyboard = create_inline_keyboard(recorder[1])
#         try:
#             photo = InputFile(os.path.join('commercial_proposal', 'images', 'recorder', data['brand'],
#                                            recorder[1].replace('/', '') + '.jpg'))
#         except Exception as e:
#             print(e)
#             continue
#         await message.answer_photo(
#             photo=photo,
#             caption=f'{recorder[1]}\nЦена: {recorder[2]}, Оптовая: {recorder[3]}',
#             reply_markup=keyboard)


@dp.callback_query_handler(choice_reg_callback.filter(make='show'), state=RegSelections.q_3)
async def step_6(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=5)
    recorder = db.get_equipment_data_by_model('DataRecorder', 'model, description, specifications, price',
                                              callback_data.get('model'))
    caption = f'{recorder[0]}\n' \
              f'{recorder[1]}\n' \
              f'{recorder[2]}\n' \
              f'Цена: {recorder[3]}₽'
    keyboard = create_inline_keyboard_2(callback_data.get('model'))
    try:
        await call.message.edit_caption(caption=caption, reply_markup=keyboard)
    except BadRequest as e:
        await call.message.edit_text(text=caption, reply_markup=keyboard)


@dp.callback_query_handler(choice_reg_callback.filter(make='choice'), state=RegSelections.q_3)
async def step_7(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=30)
    data = await state.get_data()
    logger.debug(data)
    data.update({'id_tg': call.from_user.id, 'model': callback_data.get('model')})
    data.pop('options')
    data.pop('brand')
    data_for_del = data.copy()
    data_for_del.pop('model')
    columns = ', '.join(data.keys())
    # return
    db.insert_choice_equipment('ChoiceRecorder', columns, data, data_for_del)
    await call.message.edit_reply_markup()
    await call.message.answer(f'Вы выбрали {callback_data.get("model")}', reply_markup=keyboards.menu_video)
    await state.finish()
