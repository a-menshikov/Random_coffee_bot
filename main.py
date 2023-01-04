import sqlite3
from data.config import dp, bot
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


if __name__ == '__main__':
    path = 'data/coffee_database.db'
    db_controller = DatabaseManager(path)
    db_controller.create_tables()
    executor.start_polling(dp, skip_updates=True)

