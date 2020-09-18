from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

menu = ReplyKeyboardMarkup([
    [KeyboardButton(text='Договор на монтаж видеонаблюдения')],
    [KeyboardButton(text='Изменить данные исполнителя')],
    [KeyboardButton(text='Изменить свои данные')]
], resize_keyboard=True)

yes_or_no = ReplyKeyboardMarkup([
    [KeyboardButton(text='Да')],
    [KeyboardButton(text='Нет')],
    [KeyboardButton(text='Отмена')]
], resize_keyboard=True)

key_cancel = ReplyKeyboardMarkup([
    [KeyboardButton(text='Отмена')]
], resize_keyboard=True)

phone_key = ReplyKeyboardMarkup([[KeyboardButton(text='Отправить свой номер', request_contact=True)]],
                                resize_keyboard=True)
