from typing import Union

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

import db

choice_reg_callback = CallbackData('choice', 'model', 'make')


def create_keyboard_reg_and_switch(column: str, table: str, filters: dict = None) -> Union[bool, tuple]:
    buttons = db.get_equipments_types(column, table, filters)
    if not buttons:
        return False
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for button in buttons:
        keyboard.add(KeyboardButton(text=button))
    keyboard.add(KeyboardButton(text='↩️Отмена'))

    return keyboard, buttons


def create_inline_keyboard(model: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    button_choice = InlineKeyboardButton(
        text='Выбрать',
        callback_data=choice_reg_callback.new(model=model, make='choice'))
    button_show = InlineKeyboardButton(
        text='Детали',
        callback_data=choice_reg_callback.new(model=model, make='show'))
    keyboard.insert(button_show)
    keyboard.insert(button_choice)

    return keyboard


def create_inline_keyboard_2(model: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    button_choice = InlineKeyboardButton(
        text='Выбрать',
        callback_data=choice_reg_callback.new(model=model, make='choice'))

    keyboard.insert(button_choice)
    return keyboard
