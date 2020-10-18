from aiogram import types
from misc import dp


@dp.message_handler(content_types=types.ContentTypes.ANY)
async def all_other_message(message: types.Message):
    # print(message)
    await message.answer('Введите команду /start')
    # await message.answer(message)
