import asyncio
import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import db
import work_with_api
from create_contract import filling_contract
from misc import dp


class FillingContract(StatesGroup):  # информация о клиенте
    inn = State()  # ИНН
    address = State()  # адрес
    price = State()  # цена
    prepaid_expense = State()  # аванс
    period = State()  # Срок выполнения работы
    bik = State()  # БИК Банка
    current_account = State()  # Рассчетный счет клиента
    answer = State()
    api_inn_ = State()
    api_bik_ = State()


@dp.message_handler(lambda message: message.text == 'Договор на монтаж видеонаблюдения')
async def start_create_contract(message: types.Message):
    await message.answer('Введи ИНН клиента', reply_markup=types.ReplyKeyboardRemove())
    await FillingContract.inn.set()


@dp.message_handler(state=FillingContract.inn, content_types=types.ContentTypes.TEXT)
async def filling_step_1(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Некорректный ИНН. ИНН должен состоять только из цифр')
        return
    data_from_api = work_with_api.parse_answer_inn(message.text)
    if not data_from_api:
        await message.answer('Неверный ИНН. Укажи верный')
        return
    # data_from_api = work_with_api.parse_answer_inn(message.text)
    await state.update_data(inn=message.text)
    await state.update_data(api_inn_=data_from_api)
    # await FillingContract.next()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text='Да', callback_data=f'yes {message.text}'),
                 types.InlineKeyboardButton(text='Нет', callback_data='no'))
    await message.answer(f"Монтаж будет проходить по адресу: {data_from_api[0]['address']}?", reply_markup=keyboard)


@dp.callback_query_handler(state=FillingContract.inn)
async def proof_of_address(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data[0] == 'y':
        inn = callback_query.data.split()[-1]
        await state.update_data(address=work_with_api.parse_answer_inn(inn)[0]['address'])
        await FillingContract.price.set()
        await callback_query.message.edit_reply_markup()
        await callback_query.message.answer('Укажи общую стоимость монтажа в договоре в рублях (только цифры)')
    else:
        await FillingContract.next()
        await callback_query.message.edit_reply_markup()
        await callback_query.message.answer('Напиши адрес по которому будет проходить монтаж')


@dp.message_handler(state=FillingContract.address, content_types=types.ContentTypes.TEXT)
async def filling_step_2(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await FillingContract.next()
    await message.answer('Укажи общую стоимость монтажа в договоре в рублях (только цифры)')


@dp.message_handler(state=FillingContract.price, content_types=types.ContentTypes.TEXT)
async def filling_step_3(message: types.Message, state: FSMContext):
    price = message.text.replace(',', '.')
    if not price.replace('.', '').isdigit():
        await message.answer('Укажи стоимость используя только цифры')
        return
    await state.update_data(price=price)
    await FillingContract.next()
    await message.answer('Какой будет аванс в %, если без аванса, то напиши 100')


@dp.message_handler(state=FillingContract.prepaid_expense, content_types=types.ContentTypes.TEXT)
async def filling_step_4(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Введи аванс используя только цифры')
        return
    await state.update_data(prepaid=message.text)
    await FillingContract.next()
    await message.answer('Какой срок выполнения работ в днях?')


@dp.message_handler(state=FillingContract.period, content_types=types.ContentTypes.TEXT)
async def filling_step_5(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Напиши только цифры')
        return
    await state.update_data(period=message.text)
    await FillingContract.next()
    await message.answer('Напиши БИК банка клиента')


@dp.message_handler(state=FillingContract.bik, content_types=types.ContentTypes.TEXT)
async def filling_step_6(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Некорректный БИК')
        return

    api_bik = work_with_api.parse_answer_bik(message.text)
    if not api_bik:
        await message.answer('Неверный БИК. Укажи верный')
        return

    await state.update_data(bik=message.text)
    await state.update_data(api_bik_=api_bik)
    await FillingContract.next()
    await message.answer('Верно укажи номер расчетного счета клиента')


@dp.message_handler(state=FillingContract.current_account, content_types=types.ContentTypes.TEXT)
async def filling_step_7(message: types.Message, state: FSMContext):
    data = await state.get_data()
    api_inn = data['api_inn_']
    if api_inn[1] == 'ИП':
        name = api_inn[0]['name_ip']
    else:
        name = api_inn[0]['name_org']
    api_bik = data['api_bik_']
    await state.update_data(api_bik_=api_bik)
    await state.update_data(current_account=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add('Да')
    keyboard.add('Нет')
    await FillingContract.next()
    await message.answer(f"Проверь данные клиента:\n"
                         f"ИНН: {data['inn']}\n"
                         f"{name}\n"
                         f"Адрес: {data['address']}\n"
                         f"Цена руб.: {data['price']}\n"
                         f"Аванс: {data['prepaid']} %\n"
                         f"Срок выполнения, дней: {data['period']}\n"
                         f"Расчетный счет: {message.text}\n"
                         f"Корреспондентский счет: {api_bik['number_account']}\n"
                         f"БИК: {data['bik']}\n"
                         f"Банк {api_bik['name_bank']}\n"
                         f"Все верно?", reply_markup=keyboard)


@dp.message_handler(state=FillingContract.answer, content_types=types.ContentTypes.TEXT)
async def filling_step_8(message: types.Message, state: FSMContext):
    if message.text == 'Нет':
        await FillingContract.inn.set()
        await message.answer('Введи инн клиента', reply_markup=types.ReplyKeyboardRemove())
    else:
        data = await state.get_data()
        await message.answer('Я начал составлять договор. Обычно это занимает не больше 1 минуты.',
                             reply_markup=types.ReplyKeyboardRemove())
        filling_contract(data, message.from_user.id)
        number = db.get_number_contract(message.from_user.id)
        await state.finish()
        await asyncio.sleep(40)

        file = types.InputFile(f'Договор.docx')
        await message.answer_document(document=file)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Договор на монтаж видеонаблюдения')
        keyboard.add('Изменить реквизиты исполнителя')
        keyboard.add('Изменить свои данные')
        await message.answer('Договор готов! Что дальше?', reply_markup=keyboard)
        db.update_number_account(message.from_user.id)
        os.remove('Договор.docx')
