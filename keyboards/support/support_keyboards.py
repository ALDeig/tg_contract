from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

confirm_order = CallbackData("confirm", "number_order", "phone", "id_provider")
answer_of_provider = CallbackData('answer', 'id_tg', 'number_order')


cancel_connection = ReplyKeyboardMarkup([
    [KeyboardButton(text='Закончить отправку')],
    [KeyboardButton(text='↩ Отмена')]
], resize_keyboard=True)


def create_keyboard(phone, number_order, id_provider):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text='Подтвердить заказ',
            callback_data=confirm_order.new(
                phone=phone,
                number_order=number_order,
                id_provider=id_provider))
    )
    return keyboard


def keyboard_for_provider(id_tg, number_order):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text='Ответить на заказ',
                             callback_data=answer_of_provider.new(id_tg=id_tg, number_order=number_order))
    )
    return keyboard
