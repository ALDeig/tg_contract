from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import analytics
from misc import dp
import db
import keyboards
import work_with_api


class DataRegistrationUser(StatesGroup):
    name = State()
    city = State()
    phone = State()
    answer = State()


class DataRegistrationExecutor(StatesGroup):
    inn = State()  # ИНН
    form_of_taxation = State()  # Форма налогооблажения
    bik = State()  # БИК Банка
    checking_account = State()  # Расчетный счет
    warranty_period = State()  # Гарантия на работы в мес
    contract_number = State()  # Номер договора с которого начнется отсчет
    answer = State()


@dp.message_handler(text='Регистрация', state='*')
@dp.message_handler(text='👨‍🔧 Изменить свои данные', state='*')
async def start_registration(message: types.Message):
    info = db.get_info('name, city, phone', 'users', message.from_user.id, 'id_tg')
    if info:
        text = f'Текущие данные:\n'\
               f'Имя: {info[0]}\n'\
               f'Город: {info[1]}\n'\
               f'Телефон: {info[2]}'
        await message.answer(text)
    await message.answer('Как тебя зовут?', reply_markup=keyboards.key_cancel)
    await DataRegistrationUser.name.set()


@dp.message_handler(state=DataRegistrationUser.name)
async def reg_step_1(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.capitalize())
    await DataRegistrationUser.next()
    await message.answer('Из какого ты города?')


@dp.message_handler(state=DataRegistrationUser.city)
async def reg_step_2(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text.capitalize())
    await DataRegistrationUser.next()
    await message.answer('Введи номер телефона (без пробелов, скобок и тире, начни с 7)',
                         reply_markup=keyboards.phone_key)


@dp.message_handler(state=DataRegistrationUser.phone, content_types=types.ContentTypes.CONTACT)
async def reg_step_3(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone.replace('+', ''))
    user_data = await state.get_data()
    await DataRegistrationUser.next()
    await message.answer(f"Проверь данные:\n"
                         f"Имя: {user_data['name']}\n"
                         f"Город: {user_data['city']}\n"
                         f"Телефон: {user_data['phone']}\n"
                         f"Все верно?", reply_markup=keyboards.yes_or_no)


@dp.message_handler(state=DataRegistrationUser.phone, content_types=types.ContentTypes.TEXT)
async def reg_step_3(message: types.Message, state: FSMContext):
    if not message.text[1:].isdigit() or len(message.text) != 11:
        await message.answer('Некорректный номер')
        return
    await state.update_data(phone=message.text)
    user_data = await state.get_data()
    await DataRegistrationUser.next()
    await message.answer(f"Проверь данные:\n"
                         f"Имя: {user_data['name']}\n"
                         f"Город: {user_data['city']}\n"
                         f"Телефон: {user_data['phone']}\n"
                         f"Все верно?", reply_markup=keyboards.yes_or_no)


@dp.message_handler(state=DataRegistrationUser.answer)
async def reg_step_4(message: types.Message, state: FSMContext):
    if message.text == 'Да':
        if db.check_user_in(message.from_user.id, 'id_tg', 'users'):
            type_executor = db.get_type_executor(id_tg=message.from_user.id)
            number_kp = db.get_number_kp(id_tg=message.from_user.id)
        else:
            type_executor = None
            number_kp = 1
        db.delete_user(message.from_user.id)
        user_data = await state.get_data()
        user_data.update({'id_tg': message.from_user.id, 'number_kp': number_kp})
        columns = ['name', 'city', 'phone', 'id_tg', 'number_kp']
        db.insert('users', columns, user_data)
        if type_executor:
            db.update_type_executor(type_executor=type_executor, id_tg=message.from_user.id)

        await state.finish()
        await message.answer('Выберите действие', reply_markup=keyboards.menu)
    else:
        await state.finish()
        await message.answer('Как тебя зовут?', reply_markup=keyboards.key_cancel)
        await DataRegistrationUser.name.set()


def get_info(table: str, id_tg: int, type_executor: str) -> str or bool:
    if type_executor == 'ИП':
        columns = ', '.join(['name_ip', 'inn', 'ogrn', 'address', 'bik', 'name_bank', 'warranty'])
    else:
        columns = ', '.join(['name_org', 'inn', 'ogrn', 'address', 'bik', 'name_bank', 'warranty'])

    info = db.get_info(columns, table, id_tg, 'user_id_tg')
    if not info:
        return False
    text = f'Текущие данные:\nИмя: {info[0]}\nИНН: {info[1]}\nОГРН: {info[2]}\nАдрес: {info[3]}\n' \
           f'БИК: {info[4]}\nБанк: {info[5]}\nГарантия: {info[6]}'
    return text


@dp.message_handler(text='Регистрация исполнителя', state='*')
@dp.message_handler(text='🏢 Изменить данные исполнителя', state='*')
async def start_registration_executor(message: types.Message):
    if message.text == '🏢 Изменить данные исполнителя':
        type_executor = db.get_type_executor(message.from_user.id)
        table = 'executor_ip' if type_executor == 'ИП' else 'executor_ooo'
        info = get_info(table, message.from_user.id, type_executor)
        if info:
            await message.answer(info)
        else:
            await message.answer('Введите данные')
    await message.answer('Введи ИНН исполнителя', reply_markup=keyboards.key_cancel)
    await DataRegistrationExecutor.inn.set()


@dp.message_handler(state=DataRegistrationExecutor.inn)
async def reg_step_1(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Некоректный ИНН')
        return

    api_inn = work_with_api.parse_answer_inn(message.text)
    if not api_inn:
        await message.answer('Неверный ИНН. Укажи верный')
        return
    analytics.insert_data('request_inn')
    await state.update_data(inn=message.text)
    await state.update_data(api_inn=api_inn)
    await DataRegistrationExecutor.next()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text='Без НДС', callback_data='usi'),
                 types.InlineKeyboardButton(text='С НДС 20%', callback_data='osno'))
    await message.answer('Работаешь с НДС?', reply_markup=keyboard)


@dp.callback_query_handler(state=DataRegistrationExecutor.form_of_taxation)
async def reg_step2(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'usi':
        await state.update_data(form='упрощенную систему налогообложения')
    else:
        await state.update_data(form='общую систему налогообложения')
    await DataRegistrationExecutor.next()
    await callback_query.message.edit_reply_markup()
    await callback_query.message.answer(text='Введи БИК банка')


@dp.message_handler(state=DataRegistrationExecutor.bik)
async def reg_step_6(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Некорректный БИК')
        return

    api_bik = work_with_api.parse_answer_bik(message.text)
    analytics.insert_data('request_bik')
    if not api_bik:
        await message.answer('Неверный БИК. Укажи верный')
        return

    await state.update_data(bik=message.text)
    await state.update_data(api_bik=api_bik)
    await DataRegistrationExecutor.next()
    await message.answer('Верно укажи номер расчётного счёта')


@dp.message_handler(state=DataRegistrationExecutor.checking_account)
async def reg_step_7(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or len(message.text) != 20:
        await message.answer('Видимо не верно указал номер счета. Проверь и введи верный номер.')
        return

    await state.update_data(check_account=message.text)
    await DataRegistrationExecutor.next()
    await message.answer('Какую гарантию в месяцах на работы указывать в договоре?')


@dp.message_handler(state=DataRegistrationExecutor.warranty_period)
async def reg_step_8(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Введите число')
        return
    await state.update_data(warranty=message.text)
    await DataRegistrationExecutor.next()
    await message.answer('Напиши номер договора (последним символом договора должна быть цифра). Тебе не надо будет '
                         'вводить его каждый раз, я буду прибавлять к новому договору единицу')


@dp.message_handler(state=DataRegistrationExecutor.contract_number)
async def reg_step_9(message: types.Message, state: FSMContext):
    if not message.text[-1].isdigit():
        await message.answer('Номер договора должен заканчиваться цифрой')
        return

    await state.update_data(number=message.text)
    executor_data = await state.get_data()
    answer_api_inn = executor_data['api_inn']
    answer_api_bik = executor_data['api_bik']
    await DataRegistrationExecutor.next()
    if executor_data['form'][0] == 'у':
        form = 'Без НДС'
    else:
        form = 'С НДС 20%'
    await message.answer(f"Ваши данные:\n"
                         f"ИНН: {executor_data['inn']}\n"
                         f"{answer_api_inn[0]['name_ip']}\n"
                         f"{form}\n"
                         f"БИК: {executor_data['bik']}\n"
                         f"Банк: {answer_api_bik['name_bank']}\n"
                         f"Рассчетный счет: {executor_data['check_account']}\n"
                         f"Корресподентский счет: {answer_api_bik['number_account']}\n"
                         f"Гарантия: {executor_data['warranty']}\n"
                         f"Номер договора: {executor_data['number']}\n"
                         f"Все верно?", reply_markup=keyboards.yes_or_no)


@dp.message_handler(state=DataRegistrationExecutor.answer)
async def reg_step_10(message: types.Message, state: FSMContext):
    if message.text == 'Да':
        db.delete(message.from_user.id)
        data = await state.get_data()
        if data['api_inn'][1] == 'ЮЛ':
            db.update_type_executor(type_executor='ЮЛ', id_tg=message.from_user.id)
            columns = ['name_org', 'initials', 'position_in_org', 'ogrn', 'kpp', 'address', 'name_bank',
                       'number_account', 'inn', 'form', 'bik', 'check_acc', 'warranty', 'number_contract', 'user_id_tg']
            data = db.create_data_to_db(data=data)
            data.update({'user_id_tg': message.from_user.id})
            db.insert('executor_ooo', columns, data=data)
        else:
            db.update_type_executor(type_executor='ИП', id_tg=message.from_user.id)
            columns = ['name_ip', 'ogrn', 'type_ip', 'code_region', 'address', 'name_bank', 'cor_account', 'inn',
                       'form', 'bik', 'check_acc', 'warranty', 'number_contract', 'user_id_tg']
            data = db.create_data_to_db(data=data)
            data.update({'user_id_tg': message.from_user.id})
            db.insert('executor_ip', columns, data)
        await state.finish()
        await message.answer(text='Вот и всё, я запомнил данные исполнителя. Если надо будет их изменить нажми кнопку '
                                  '“Изменить данные Исполнителя”. А сейчас давай сформируем первый договор, выбери '
                                  'какой.', reply_markup=keyboards.menu)
    else:
        await state.finish()
        await message.answer('Введи ИНН исполнителя', reply_markup=keyboards.key_cancel)
        await DataRegistrationExecutor.inn.set()
