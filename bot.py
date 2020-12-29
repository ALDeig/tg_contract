from aiogram import executor, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from commercial_proposal.parser_prices import save_prices
# from commercial_proposal import parser
from misc import dp
import handlers


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("get_analytics", "Получить аналитику (только для администратора)"),
        types.BotCommand("document", "Изменить ответ на кнопку Документы (только для администратора)"),
        types.BotCommand("get_reviews", "Отзывы (только для администратора)"),
        types.BotCommand("send_message", "Отправить сообщение всем пользователям (только для администратора)"),
        types.BotCommand("get_limit", "Остаток ИНН и БИК (только для администартора)"),
        types.BotCommand("save_cameras", "Сохранить данные из таблицы в базу (только для админа)")
    ])


scheduler = AsyncIOScheduler()
scheduler.add_job(save_prices, 'cron', day='*', hour='7', minute='00')

if __name__ == '__main__':
    # save_prices()
    # parser.insert_information()
    # scheduler.start()
    executor.start_polling(dp, skip_updates=True, on_startup=set_default_commands)
