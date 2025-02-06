from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from handlers.user.first_check import check_and_add_registration_button
from loader import logger


# @dp.message_handler(commands=['start', 'help'], state='*')
async def process_start_command(message: types.Message, state: FSMContext):
    """Функция первого обращения к боту."""
    await state.reset_state()
    logger.info(
        f"user id-{message.from_user.id} "
        f"tg-@{message.from_user.username} start a bot"
    )
    await check_and_add_registration_button(message)


def register_start_handler(dp: Dispatcher):
    dp.register_message_handler(
        process_start_command, commands=["start", "help"], state="*"
    )
