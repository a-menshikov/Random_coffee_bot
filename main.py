import asyncio

import aioschedule
from aiogram import executor, types

from data import ADMIN_TG_ID

from handlers.user.check_message import check_message
from handlers.user.holidays import sheduled_check_holidays
from keyboards import algo_start
from loader import bot, logger
from match_algoritm import MachingHelper

from handlers.decorators import admin_handlers
from handlers.user import *
# from handlers.user.unknown_message import dp


@dp.message_handler(text=algo_start)
@admin_handlers
async def start_algoritm(message: types.Message):
    """Запуск алгоритма распределения"""
    await check_message()
    mc.prepare()
    res = mc.start()
    await mc.send_and_write(res)


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
    mc = MachingHelper()
    executor.start_polling(dp, skip_updates=True,
                           on_startup=on_startup,
                           on_shutdown=on_shutdown
                           )
