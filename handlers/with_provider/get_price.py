from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ContentTypes

import config
import db
from keyboards import keyboards
from misc import dp


@dp.message_handler(text='🚚 Поставщикам')
async def send_menu_for_provider(message: Message):
    keyboard = keyboards.price
    await message.answer('Выберите действие', reply_markup=keyboard)


@dp.message_handler(text='Загрузить прайс')
async def get_price_1(message: Message, state: FSMContext):
    await message.answer('Отправьте файл прайс-листа', reply_markup=keyboards.key_cancel)
    await state.set_state('send_price')


@dp.message_handler(content_types=ContentTypes.DOCUMENT, state='send_price')
async def send_price_to_provider(message: Message, state: FSMContext):
    user = db.get_data('name, city', 'users', {'id_tg': ('=', message.from_user.id)})[0]
    await dp.bot.send_message(chat_id=config.ADMIN_ID[0], text=f'Прайс от поставщика:\n{user.name}\n{user.city}')
    await message.copy_to(config.ADMIN_ID[0])
    await message.answer('Готово', reply_markup=keyboards.menu)
    await state.finish()
