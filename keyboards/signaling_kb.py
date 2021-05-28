from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData

callback_safe = CallbackData('security', 'security_type', 'value')
callback_devices = CallbackData('security', 'security_type', 'value')

choice_marks = {1: "✅", 0: "⛔"}
dict_category = {
    'intrusion_protection': 'Защита от вторжения',
    'fire_safety': 'Пожарная безопасность',
    'leakage_protection': 'Защита от протечек',
    'street_guard': 'Охрана улицы'
}

additional_devices = {
    'intrusion_protection': 'Защита от вторжения',
    'fire_safety': 'Пожарная безопасность',
    'leakage_protection': 'Защита от протечек',
    'siren': 'Сирены',
    'control': 'Управление',
    'automation': 'Автоматизация',
    'repeaters': 'Ретрансляторы'
}
# [KeyboardButton(text='Ретрансляторы')
additional_devices_kb = ReplyKeyboardMarkup([
    [KeyboardButton(text='Защита от вторжения'), KeyboardButton(text='Пожарная безопасность')],
    [KeyboardButton(text='Защита от протечек'), KeyboardButton(text='Сирены')],
    [KeyboardButton(text='Управление'), KeyboardButton(text='Автоматизация')],
    [KeyboardButton(text='Ретрансляторы')],
    [KeyboardButton(text='Сформировать КП')]
], resize_keyboard=True)


def create_kb_safe(categories: dict):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for key, value in categories.items():
        keyboard.add(InlineKeyboardButton(
            text=f'{choice_marks.get(value)} {dict_category.get(key)}',
            callback_data=callback_safe.new(
                security_type=key,
                value=value
            )
        ))
    return keyboard


def create_kb_additional_devices(devices: dict):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for key, value in devices.items():
        keyboard.add(InlineKeyboardButton(
            text=f'{choice_marks.get(value)} {additional_devices.get(key)}',
            callback_data=callback_devices.new(
                security_type=key,
                value=value
            )
        ))
    return keyboard


floors_kb = ReplyKeyboardMarkup([
    [KeyboardButton(text='Первый'), KeyboardButton(text='Второй')],
    [KeyboardButton(text='Последний'), KeyboardButton(text='Другой')],
    [KeyboardButton(text='↩️Отмена')]
], resize_keyboard=True)

devices_selection = ReplyKeyboardMarkup([
    [KeyboardButton(text='Хаб'), KeyboardButton(text='Вторжение')],
    [KeyboardButton(text='Пожар'), KeyboardButton(text='Протечка')],
    [KeyboardButton(text='Управление'), KeyboardButton(text='Сирена')],
    [KeyboardButton(text='ББП'), KeyboardButton(text='↩️Отмена')]
], resize_keyboard=True)


def selection_keyboard(table):
    pass

