from typing import Union

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

import db


def create_keyboard_hdd():
    buttons = db.get_equipments_types('brand', 'DataHDD')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for button in buttons:
        keyboard.add(KeyboardButton(text=button))
    keyboard.add(KeyboardButton(text='↩️Отмена'))

    return keyboard, buttons
