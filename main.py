import asyncio

import aioschedule
from aiogram import executor, types
from data import ADMIN_TG_ID
from handlers.admin import FSMContext
from handlers.user import (check_message, check_user_in_base,
                           sheduled_check_holidays)
from handlers.user.ban_check import check_user_in_ban
from keyboards import (admin_main_markup, algo_start, main_markup,
                       start_registr_markup)
from loader import bot, dp, logger
from match_algoritm import MachingHelper
from states import AdminData, BannedState, UserData


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
        text=f'Привет, {name}. У нас вот такой бот. "Регламент".',
    )
    await check_and_add_registration_button(message)


@dp.message_handler(text=algo_start, state=AdminData.start)
async def start_algoritm(message: types.Message, state: FSMContext):
    """Запуск алгоритма распределения"""
    await check_message(state)
    mc.prepare()
    res = mc.start()
    print("retunr-", res)
    await mc.send_and_write(res)


async def check_and_add_registration_button(message: types.Message):
    """Проверка пользователя для последующих действий."""
    if message.from_user.id in list(map(int, ADMIN_TG_ID.split())):
        await bot.send_message(
            message.from_user.id,
            text="Привет, Админ. Добро пожаловать в меню администратора",
            reply_markup=admin_main_markup(),
        )
    elif not await check_user_in_base(message):
        await bot.send_message(
                message.from_user.id,
                text="Нажмите кнопку регистрации для старта.",
                reply_markup=start_registr_markup()
            )
        await UserData.start.set()

    else:
        if not await check_user_in_ban(message):
            await bot.send_message(
                message.from_user.id,
                text="Нажмите кнопку меню и выберите из доступных вариантов",
                reply_markup=main_markup(),
            )
        else:
            await bot.send_message(
                message.from_user.id,
                text="К сожалению вы нарушили наши правила и попали в бан. "
                     "Для решения данного вопроса просим обратиться к "
                     "администратору",
            )
            await BannedState.start.set()


async def scheduler():
    """Расписание выполнения задач."""
    aioschedule.every().day.at("23:19").do(sheduled_check_holidays)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    """Создание задания."""
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())

if __name__ == '__main__':
    mc = MachingHelper()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
