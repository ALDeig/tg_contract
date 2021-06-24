from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

choice_cameras_callback = CallbackData('choise', 'model', 'make')
actions = CallbackData('actions', 'make')

inline_yes_or_no = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Заказть оборудование', callback_data=actions.new(make='Yes')),
)


def create_keyboard(model):
    keyboard = InlineKeyboardMarkup(row_width=2)
    button_choice = InlineKeyboardButton(text='Выбрать',
                                         callback_data=choice_cameras_callback.new(model=model, make='choice'))
    button_show = InlineKeyboardButton(text='Детали',
                                       callback_data=choice_cameras_callback.new(model=model, make='show'))
    keyboard.insert(button_show)
    keyboard.insert(button_choice)

    return keyboard


def create_keyboard_2(model):
    keyboard = InlineKeyboardMarkup()
    button_choice = InlineKeyboardButton(text='Выбрать',
                                         callback_data=choice_cameras_callback.new(model=model, make='choice'))

    keyboard.insert(button_choice)
    return keyboard
