import sqlite3

import aioschedule
import asyncio

from loader import bot, dp
from aiogram import executor, types
from controllerBD import DatabaseManager
from keyboards.user import *
from states import UserData
from handlers.user import *



@dp.message_handler(commands=['start', 'help'])
async def process_start_command(message: types.Message, state: FSMContext):
    """Функция первого обращения к боту."""
    name = message.from_user.full_name
    await bot.send_message(
        message.from_user.id,
        text=f'Привет, {name}. У нас вот такой бот. "Регламент".',
    )
    await check_and_add_registration_button(message)


async def check_and_add_registration_button(message: types.Message):
    if not await check_user_in_base(message):
        await bot.send_message(
            message.from_user.id,
            text="Нажмите кнопку регистрации для старта.",
            reply_markup=start_registr_markup()
        )
        await UserData.start.set()
    else:
        await bot.send_message(
            message.from_user.id,
            text="Нажмите кнопку меню и выберите из доступных вариантов",
            reply_markup=main_markup(),
        )

async def scheduler():
    aioschedule.every().day.at("00:22").do(sheduled_check_holidays)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())

if __name__ == '__main__':
    path = 'data/coffee_database.db'
    db_controller = DatabaseManager(path)
    db_controller.create_tables()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

