from aiogram import types

from handlers.decorators import user_handlers
from keyboards.user import menu_markup
from loader import dp, bot


@dp.message_handler(state="*")
@user_handlers
async def unknown_message(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        "Я Вас не понимаю. Пожалуйста воспользуйтесь меню.",
        reply_markup=menu_markup(message)
    )
