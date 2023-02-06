from aiogram import types
from aiogram.types import InputFile

from handlers.decorators import user_handlers
from keyboards.user import menu_markup
from loader import dp, bot


@dp.message_handler(state="*")
@user_handlers
async def unknown_message(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        ("Я Вас не понимаю. Пожалуйста воспользуйтесь меню.\n"
         "Если меню не видно - скорее всего, оно скрыто самим Телеграмом. "
         "Открыть его можно нажав в вашем мессенджере кнопку обведенную "
         "красным квадратом."),
        reply_markup=menu_markup(message)
    )
    photo = InputFile("files/help_image.jpg")
    await bot.send_photo(
        message.from_user.id,
        photo=photo
    )
