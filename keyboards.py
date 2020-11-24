from aiogram.types import KeyboardButton, ReplyKeyboardMarkup  # MediaGroup

menu = ReplyKeyboardMarkup([
    [KeyboardButton(text='📑 Договор на монтаж видеонаблюдения')],
    [KeyboardButton(text='💰 Создать КП')],
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
    [KeyboardButton(text='Купольная')],
    [KeyboardButton(text='Цилиндрическая')],
    [KeyboardButton(text='Компактная')]
], resize_keyboard=True)

choice_type_cam_outdoor = ReplyKeyboardMarkup([
    [KeyboardButton(text='Купольная')],
    [KeyboardButton(text='Цилиндрическая')]
], resize_keyboard=True)

menu_kp = ReplyKeyboardMarkup([
    [KeyboardButton(text='🎥 Видеонаблюдение')],
    [KeyboardButton(text='📤 Загрузить шаблон КП')],
    [KeyboardButton(text='↩️Отмена')]
], resize_keyboard=True)

reviews_key = ReplyKeyboardMarkup([
    [KeyboardButton(text='Еще')],
    [KeyboardButton(text='↩️Отмена')]
], resize_keyboard=True)

photo_cams = 'AgACAgIAAxkBAAIEEl-Jow2lPwyzJv_gnmqhqCF_LUxAAAKOsjEbM1xQSIStmNIt9MQqVPHdly4AAwEAAwIAA20AA1SsAQABGwQ'  # в прокте
# photo_cams = 'AgACAgIAAxkBAAIZl1-DXN-SFf2DVqliESRdj9RpSvzKAAIOsDEbPYsgSOIAAfHYPTKhaxb1wJcuAAMBAAMCAANtAAOkeAEAARsE'  # у меня
