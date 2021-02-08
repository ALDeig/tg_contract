from typing import Union

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

import db


def create_keyboard_other(value, table, filters=None):
    if filters:
        buttons = db.get_equipments_types(value, table, filters)
    else:
        buttons = db.get_equipments_types(value, table)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = list(buttons)
    buttons.sort()
    for button in buttons:
        keyboard.add(KeyboardButton(text=button))
    keyboard.add(KeyboardButton(text='↩️Отмена'))

    return keyboard, buttons
