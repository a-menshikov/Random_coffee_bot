import sqlite3
from data.config import dp, bot
from aiogram import executor, types
from match_algoritm import MachingHelper
from controllerBD import DatabaseManager



@dp.message_handler(commands=['start', 'help'])
async def process_start_command(message: types.Message):
    """Функция первого обращения к боту."""
    name = message.from_user.full_name
    await bot.send_message(
        message.from_user.id,
        text=f'Привет, {name}. У нас вот такой бот. "Регламент".',
    )
    await check_and_add_registration_button(message)
    help = MachingHelper()
    res = help.start()
    await message.answer(res)


async def check_and_add_registration_button(message: types.Message):
    if not check_user_in_base(message):
        await bot.send_message(
            message.from_user.id,
            text="Нажмите кнопку регистрации для старта.",
            reply_markup=registration_keyboard
        )
    pass


def check_user_in_base(message):
    """Проверяем пользователя на наличие в БД"""
    return False


registration_keyboard = types.InlineKeyboardMarkup()

registration = types.InlineKeyboardButton(
    'Регистрация',
    callback_data='registration'
)
registration_keyboard.row(registration)


if __name__ == '__main__':
    path = 'C:/Users/User/Desktop/Programming/Data/random_coffee/data/coffee_database.db'
    db_controller = DatabaseManager(path)
    db_controller.create_tables()
    executor.start_polling(dp, skip_updates=True)

