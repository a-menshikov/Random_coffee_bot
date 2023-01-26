import asyncio

import aioschedule
from aiogram import executor, types

from data import ADMIN_TG_ID

from handlers.user.holidays import sheduled_check_holidays
from loader import bot, logger

from handlers.user.start_handler import dp
from handlers.user.new_member import dp
from handlers.user.handlers import dp
from handlers.user.help_texts import dp
from handlers.user.holidays import dp
from handlers.user.reviews import dp
from handlers.admin.ban_handlers import dp
from handlers.admin.handlers import dp
from handlers.user.unknown_message import dp
__all__ = ['dp']


async def scheduler():
    """Расписание выполнения задач."""
    aioschedule.every().day.at("12:00").do(sheduled_check_holidays)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    """Выполняется во время запуска бота."""
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())
    for i in list(map(int, ADMIN_TG_ID.split())):
        try:
            await bot.send_message(i, 'Бот запущен')
        except Exception as error:
            logger.error(f'Сообщение о запуске бота не ушло. Ошибка {error}')


async def on_shutdown(_):
    """Выполняется во время остановки бота."""
    for i in list(map(int, ADMIN_TG_ID.split())):
        try:
            await bot.send_message(i, 'Бот остановлен')
        except Exception as error:
            logger.error(f'Сообщение об остановке бота не ушло.'
                         f' Ошибка {error}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True,
                           on_startup=on_startup,
                           on_shutdown=on_shutdown
                           )
