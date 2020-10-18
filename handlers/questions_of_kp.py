import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

import asyncio
from commercial_proposal import calculate_kp, create_doc
import db
from handlers.get_cost_of_work import DataPrices
import keyboards
from misc import dp


class DataPoll(StatesGroup):
    total_numb_of_cam = State()  # total_cams
    indoor_cameras = State()  # cams_on_indoor
    cams_on_street = State()  # cams_on_street
    type_cams_in_room = State()  # type_cam_on_street
    type_cams_on_street = State()  # type_cam_in_room
    days_for_archive = State()  # days_for_archive
    answer_total_price = State()
    answer_of_sale = State()


@dp.message_handler(text='КП на камерах HiWatch')
async def start_poll(message: types.Message):
    if db.check_user_in(id_tg=message.from_user.id, column='id_tg', table='cost_work'):  # проверяет есть ли данные в базе
        await message.answer('Какое общее количество камер надо установить?', reply_markup=keyboards.key_cancel)
        await DataPoll.first()
        return
    await message.answer('Укажите стоимость монтажа 1 IP камеры, без прокладки кабеля')
    await DataPrices.first()


@dp.message_handler(state=DataPoll.total_numb_of_cam)
async def step_1(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Вы не верно указали количество. Сколько камер надо установить?')
        return
    await state.update_data(total_cams=message.text)
    await DataPoll.next()
    await message.answer('Сколько камер будет в помещении?')


@dp.message_handler(state=DataPoll.indoor_cameras)
async def step_2(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Вы не верно указали количество. Сколько камер будут установлены в помещении?')
        return
    async with state.proxy() as data:
        total_cams = data['total_cams']
        data['cams_on_indoor'] = message.text
        data['cams_on_street'] = str(int(total_cams) - int(message.text))
    if message.text == total_cams:
        await message.answer('Все камеры будут для помещения')
        await message.answer_photo(keyboards.photo_cams,
                                   caption='Какой тип камер будет установлен в помещении? Выбери варинат.',
                                   reply_markup=keyboards.choice_type_cam)
        # await message.answer_media_group(keyboards.album_1)
        # await message.answer('Какой тип камер будет установлен в помещении? Выбери варинат.',
        #                      reply_markup=keyboards.choice_type_cam)
        await DataPoll.type_cams_in_room.set()
    elif message.text == '0':
        await message.answer('Все камеры будут уличные')
        await state.update_data(type_cam_in_room=None)
        await message.answer_photo(keyboards.photo_cams,
                                   caption='Какой тип камер будет установлен на улице?',
                                   reply_markup=keyboards.choice_type_cam_outdoor)
        # await message.answer_media_group(keyboards.album_2)
        # await message.answer('Какой тип камер будет установлен на улице?',
        #                      reply_markup=keyboards.choice_type_cam_outdoor)
        await DataPoll.type_cams_on_street.set()
    else:
        # async with state.proxy() as data:
        #     total = data['total_cams']
        #     data['cams_on_indoor'] = message.text
        #     data['cams_on_street'] = int(total) - int(message.text)
        await message.answer(f'В помещении - {message.text}\nНа улице - {int(total_cams) - int(message.text)}')
        await message.answer_photo(keyboards.photo_cams,
                                   caption='Какой тип камер будет установлен в помещении? Выбери варинат.',
                                   reply_markup=keyboards.choice_type_cam)
        await DataPoll.type_cams_in_room.set()


# @dp.message_handler(state=DataPoll.cams_on_street)
# async def step_3(message: types.Message, state: FSMContext):
#     if not message.text.isdigit():
#         await message.answer('Вы не верно указали количество. Сколько камер будет установлено на улице?')
#         return
#     await state.update_data(cams_on_street=message.text)
#     await message.answer_photo('AgACAgIAAxkBAAIEEl-Jow2lPwyzJv_gnmqhqCF_LUxAAAKOsjEbM1xQSIStmNIt9MQqVPHdly4AAwEAAwIAA20AA1SsAQABGwQ',
#                                caption='Какой тип камер будет установлен в помещении?',
#                                reply_markup=keyboards.choice_type_cam)
    # await message.answer_media_group(keyboards.album_2)
    # await message.answer('Какой тип камер будет установлен в помещении?', reply_markup=keyboards.choice_type_cam)
    # await DataPoll.next()


@dp.message_handler(state=DataPoll.type_cams_in_room)
async def step_4(message: types.Message, state: FSMContext):
    await state.update_data(type_cam_in_room=message.text)
    async with state.proxy() as data:
        if data['cams_on_indoor'] == data['total_cams']:
            data['type_cam_on_street'] = None
            # data['cams_on_street'] = '0'
            await message.answer('Сколько дней будем хранить архив при записи 24/7?', reply_markup=keyboards.key_cancel)
            await DataPoll.days_for_archive.set()
            return
    await message.answer_photo(keyboards.photo_cams,
                               caption='Какой тип камер будет установлен на улице?',
                               reply_markup=keyboards.choice_type_cam_outdoor)
    # await message.answer_media_group(keyboards.album_2)
    # await message.answer('Какой тип камер будет установлен на улице?', reply_markup=keyboards.choice_type_cam_outdoor)
    await DataPoll.next()


@dp.message_handler(state=DataPoll.type_cams_on_street)
async def step_5(message: types.Message, state: FSMContext):
    await state.update_data(type_cam_on_street=message.text)
    await message.answer('Сколько дней будем хранить архив при записи 24/7?', reply_markup=keyboards.key_cancel)
    await DataPoll.next()


@dp.message_handler(state=DataPoll.days_for_archive)
async def step_6(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Вы не верно указали архив. Укажите число дней?')
        return
    await state.update_data(days_for_archive=message.text)
    data = await state.get_data()
    table_data = calculate_kp.calculate_result(data=data, id_tg=message.from_user.id)
    file_name, number_kp = create_doc.save_kp(table_data[0], table_data[1]['total'], message.from_user.id)

    await state.finish()
    await message.answer(text=f'Общая стоимость - {table_data[1]["total"]:.2f}\n'
                              f'Стоимость оборудования - {table_data[1]["equipment"]:.2f}\n'
                              f'Стоимость материалов - {table_data[1]["materials"]:.2f}\n'
                              f'Стоимость работы - {table_data[1]["work"]:.2f}', reply_markup=ReplyKeyboardRemove())
    await message.answer('Подождите, я начал формировать КП')
    await asyncio.sleep(10)
    file = types.InputFile(file_name)
    await message.answer_document(file)
    await message.answer(text='КП готов, что дальше?', reply_markup=keyboards.menu)
    db.write_number_kp(message.from_user.id, number_kp=int(number_kp) + 1)
    await asyncio.sleep(5)
    os.remove(file_name)

# "AgACAgIAAxkBAAIZl1-DXN-SFf2DVqliESRdj9RpSvzKAAIOsDEbPYsgSOIAAfHYPTKhaxb1wJcuAAMBAAMCAANtAAOkeAEAARsE" - у меня
# AgACAgIAAxkBAAIEEl-Jow2lPwyzJv_gnmqhqCF_LUxAAAKOsjEbM1xQSIStmNIt9MQqVPHdly4AAwEAAwIAA20AA1SsAQABGwQ - в проекте