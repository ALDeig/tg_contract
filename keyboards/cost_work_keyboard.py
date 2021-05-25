from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

type_system = ReplyKeyboardMarkup([
    [KeyboardButton(text='Видеонаблюдение')],
    [KeyboardButton(text='Охранная сигнализация')],
    [KeyboardButton(text='↩️Отмена')]
], resize_keyboard=True)

type_video = ReplyKeyboardMarkup([
    [KeyboardButton(text='IP')],
    [KeyboardButton(text='Аналоговая')],
    [KeyboardButton(text='↩️Отмена')]
], resize_keyboard=True)
