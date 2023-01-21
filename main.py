import asyncio

import aioschedule
from aiogram import executor, types
from aiogram.dispatcher import FSMContext

from data import ADMIN_TG_ID
from handlers.user import *
from handlers.admin import *
from handlers.user.first_check import check_and_add_registration_button
from keyboards import algo_start
from loader import bot, dp, logger
from match_algoritm import MachingHelper

from handlers.decorators import admin_handlers


@dp.message_handler(commands=['start', 'help'], state='*')
async def process_start_command(message: types.Message,
                                state: FSMContext):
    """Функция первого обращения к боту."""
    await state.reset_state()
    name = message.from_user.full_name
    logger.info(f"user id-{message.from_user.id} "
                f"tg-@{message.from_user.username} start a bot")
    await bot.send_message(
        message.from_user.id,
        text=(f"Добро пожаловать в бот для нетворкинга, {name}.\n\n"
              f"С помощью бота проходят живые и онлайн встречи 1-1 "
              f"для студентов и IT-специалистов. Каждую неделю по "
              f"понедельникам великий рандом подбирает пару. "
              f"Вам нужно самостоятельно договориться о встрече и "
              f"созвониться.  Можно встретиться лично, если вы в "
              f"одном городе.\n\nАдминистратор @Loravel")
    )
    await check_and_add_registration_button(message)


@dp.message_handler(text=algo_start)
@admin_handlers
async def start_algoritm(message: types.Message, state: FSMContext):
    """Запуск алгоритма распределения"""
    await check_message(state)
    mc.prepare()
    res = mc.start()
    await mc.send_and_write(res)


async def scheduler():
    """Расписание выполнения задач."""
    aioschedule.every().day.at("23:19").do(sheduled_check_holidays)
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
