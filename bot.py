from aiogram import executor, types

from misc import dp
import handlers


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("get_analytics", "Получить аналитику (только для администратора)"),
    ])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=set_default_commands)
