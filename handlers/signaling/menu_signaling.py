from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup

import db
from keyboards import keyboards
from misc import dp


@dp.message_handler(text='🚨 Охранная сигнализация')
async def signaling_menu(msg: Message, state: FSMContext):
    await state.set_state('signaling_menu')
    await msg.answer(text="Выберите действие", reply_markup=keyboards.menu_video)


@dp.message_handler(text='💰 Создать КП', state='signaling_menu')
async def create_kp(msg: Message, state: FSMContext):
    cost = db.get_data('id_tg', 'cost_signaling', {'id_tg': ('=', str(msg.from_user.id))})
    if not cost:
        await msg.answer(
            text='Укажите стоимость монтажа элементов охранной сигнализации (пока только оборудование Ajax)',
            reply_markup=keyboards.key_cancel)
        await msg.answer('Укажите стоимость монтажа и настройки Датчика движения')
        await state.set_state('cost_signaling')
        return
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add('Ajax', '↩️Отмена')
    await msg.answer('Выберите бренд', reply_markup=keyboard)
    await state.set_state('brand_signaling')
