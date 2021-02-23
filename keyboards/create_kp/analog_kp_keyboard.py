from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

import db


def create_keyboard_kp(column, table, filters=None):
    buttons = db.get_types(column, table, filters)
    if not buttons:
        return False
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    cnt = 1
    buttons = list(buttons)
    buttons.sort()
    for button in buttons:
        if cnt == 1:
            keyboard.add(KeyboardButton(text='🔘 ' + button if column == 'view_cam' else button))
            cnt += 1
        else:
            keyboard.insert(KeyboardButton(text='🔘 ' + button if column == 'view_cam' else button))
            cnt = 1
    keyboard.add(KeyboardButton(text='↩Отмена'))

    return keyboard, buttons
