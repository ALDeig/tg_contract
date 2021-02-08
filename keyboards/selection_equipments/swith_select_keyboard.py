from typing import Union

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

import db

choice_switch_callback = CallbackData('choice', 'model', 'make')


def create_keyboard_switch(column: str, table: str, filters: dict = None):
    buttons = db.get_equipments_types(column, table, filters)
    if not buttons:
        return False
    buttons = list(buttons)
    buttons.sort()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for button in buttons:
        keyboard.add(KeyboardButton(text=button))
    keyboard.add(KeyboardButton(text='↩️Отмена'))

    return keyboard, buttons