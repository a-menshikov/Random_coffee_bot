import asyncio

import aioschedule
from aiogram import executor

from controllerBD.services import send_message_to_admins
from handlers.admin.ban_handlers import register_admin_ban_handlers
from handlers.admin.handlers import register_admin_handlers
from handlers.user.handlers import register_user_handlers
from handlers.user.help_texts import register_help_texts_handlers
from handlers.user.holidays import register_holidays_handlers, sheduled_check_holidays
from handlers.user.new_member import register_new_member_handler
from handlers.user.review_history import register_review_history_handler
from handlers.user.reviews import register_review_handlers
from handlers.user.start_handler import register_start_handler
from handlers.user.unknown_message import register_unknown_message_handler
from loader import dp, logger
from match_algoritm.MatchingHelper import start_algoritm

register_start_handler(dp)
register_new_member_handler(dp)
register_user_handlers(dp)
register_help_texts_handlers(dp)
register_holidays_handlers(dp)
register_review_handlers(dp)
register_review_history_handler(dp)
register_admin_ban_handlers(dp)
register_admin_handlers(dp)
register_unknown_message_handler(dp)


async def scheduler():
    """Расписание выполнения задач."""
    aioschedule.every().day.at("13:00").do(sheduled_check_holidays)
    aioschedule.every().monday.at("06:37").do(start_algoritm)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    """Выполняется во время запуска бота."""
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())
    message = "Бот запущен"
    await send_message_to_admins(message)
    logger.info(message)


async def on_shutdown(_):
    """Выполняется во время остановки бота."""
    message = "Бот остановлен"
    await send_message_to_admins(message)
    logger.info(message)


if __name__ == "__main__":
    executor.start_polling(
        dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown
    )
