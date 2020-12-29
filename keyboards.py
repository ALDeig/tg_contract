from aiogram.types import KeyboardButton, ReplyKeyboardMarkup  # MediaGroup
from aiogram.utils.callback_data import CallbackData

import db

menu = ReplyKeyboardMarkup([
    [KeyboardButton(text='📑 Договор на монтаж видеонаблюдения')],
    [KeyboardButton(text='💰 Коммерческие предложение')],
    [KeyboardButton(text='🎛 Изменить данные')],
    [KeyboardButton(text='😀 Отзывы')],
    [KeyboardButton(text='🗃 Документы')]
], resize_keyboard=True)

choice_menu = ReplyKeyboardMarkup([
    [KeyboardButton(text='👨‍🔧 Изменить свои данные')],
    [KeyboardButton(text='🏢 Изменить данные исполнителя')],
    [KeyboardButton(text='⚒ Изменить стоимость работ')],
    [KeyboardButton(text='↩️Отмена')]
], resize_keyboard=True)

yes_or_no = ReplyKeyboardMarkup([
    [KeyboardButton(text='Да')],
    [KeyboardButton(text='Нет')],
    [KeyboardButton(text='↩️Отмена')]
], resize_keyboard=True)

key_cancel = ReplyKeyboardMarkup([
    [KeyboardButton(text='↩️Отмена')]
], resize_keyboard=True)

phone_key = ReplyKeyboardMarkup([[KeyboardButton(text='Отправить свой номер', request_contact=True)]],
                                resize_keyboard=True)

choice_type_cam = ReplyKeyboardMarkup([
    [KeyboardButton(text='🔘 Купольная')],
    [KeyboardButton(text='🔘 Цилиндрическая')],
    [KeyboardButton(text='🔘 Компактная')]
], resize_keyboard=True)

choice_type_cam_outdoor = ReplyKeyboardMarkup([
    [KeyboardButton(text='🔘 Купольная')],
    [KeyboardButton(text='🔘 Цилиндрическая')]
], resize_keyboard=True)

menu_kp = ReplyKeyboardMarkup([
    [KeyboardButton(text='🎥 Видеонаблюдение')],
    [KeyboardButton(text='📤 Загрузить шаблон КП')],
    [KeyboardButton(text='↩️Отмена')]
], resize_keyboard=True)

menu_video = ReplyKeyboardMarkup([
    [KeyboardButton(text='💰 Создать КП')],
    [KeyboardButton(text='⚙️Подбор оборудования')],
    [KeyboardButton(text='↩️Отмена')]
], resize_keyboard=True)

camera_selection_body = ReplyKeyboardMarkup([
    [KeyboardButton(text='🔘 Купольная')],
    [KeyboardButton(text='🔘 Цилиндрическая')],
    [KeyboardButton(text='🔘 Компактная')],
    [KeyboardButton(text='↩️Отмена')]
], resize_keyboard=True)

camera_selection_execute = ReplyKeyboardMarkup([
    [KeyboardButton(text='🏠 Внутренняя')],
    [KeyboardButton(text='⛈ Уличная')],
    [KeyboardButton(text='↩️Отмена')]
], resize_keyboard=True)

camera_selection_ppi = ReplyKeyboardMarkup([
    [KeyboardButton(text='2️⃣ 2mp')],
    [KeyboardButton(text='4️⃣ 4mp')],
    [KeyboardButton(text='↩️Отмена')]
], resize_keyboard=True)

reviews_key = ReplyKeyboardMarkup([
    [KeyboardButton(text='Еще')],
    [KeyboardButton(text='↩️Отмена')]
], resize_keyboard=True)

del_review = ReplyKeyboardMarkup([
    [KeyboardButton(text='Удалить отзыв')],
    [KeyboardButton(text='↩️Отмена')]
], resize_keyboard=True)


def create_keyboard_kp(column, filters=None):
    buttons = db.get_camera_types(column, filters)
    if not buttons:
        return False
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for button in buttons:
        keyboard.add(KeyboardButton(text='🔘 ' + button if column == 'view_cam' else button))
    keyboard.add(KeyboardButton(text='↩️Отмена'))

    return keyboard, buttons


# photo_cams = 'AgACAgIAAxkBAAIEEl-Jow2lPwyzJv_gnmqhqCF_LUxAAAKOsjEbM1xQSIStmNIt9MQqVPHdly4AAwEAAwIAA20AA1SsAQABGwQ'  # в прокте
photo_cams = 'AgACAgIAAxkBAAIZl1-DXN-SFf2DVqliESRdj9RpSvzKAAIOsDEbPYsgSOIAAfHYPTKhaxb1wJcuAAMBAAMCAANtAAOkeAEAARsE'  # у меня
