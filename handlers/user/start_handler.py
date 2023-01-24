from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.user.first_check import check_and_add_registration_button
from loader import logger, bot, dp


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
