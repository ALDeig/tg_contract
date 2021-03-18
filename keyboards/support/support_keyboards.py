from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

confirm_order = CallbackData("confirm", "number_order", "phone")
answer_of_provider = CallbackData('answer', 'id_tg', 'number_order')


def create_keyboard(phone, number_order='Неизвестен'):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text='Подтвердить заказ',
                             callback_data=confirm_order.new(phone=phone, number_order=number_order))
    )
    return keyboard


def keyboard_for_provider(id_tg, number_order):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text='Ответить на заказ',
                             callback_data=answer_of_provider.new(id_tg=id_tg, number_order=number_order))
    )
    return keyboard
