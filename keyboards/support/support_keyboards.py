from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

confirm_order = CallbackData("confirm", "number_order")


def create_keyboard(number_order='Неизвестен'):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text='Подтвердить заказ', callback_data=confirm_order.new(number_order=number_order))
    )
    return keyboard
