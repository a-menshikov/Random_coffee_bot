from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.user.first_check import check_and_add_registration_button
from loader import logger, dp


@dp.message_handler(commands=['start', 'help'], state='*')
async def process_start_command(message: types.Message,
                                state: FSMContext):
    """Функция первого обращения к боту."""
    await state.reset_state()
    logger.info(f"user id-{message.from_user.id} "
                f"tg-@{message.from_user.username} start a bot")
    await check_and_add_registration_button(message)
