from aiogram import types
from handlers.decorators import admin_handlers
from keyboards.admin import admin_menu_button, admin_menu_markup, go_back, inform
from loader import bot, dp


@dp.message_handler(text=go_back)
@admin_handlers
async def go_back(message: types.Message):
    """Возврат в меню админа."""
    await admin_menu(message)


@dp.message_handler(text=admin_menu_button)
@admin_handlers
async def admin_menu(message: types.Message):
    """Вывод меню администратора."""
    await bot.send_message(
        message.from_user.id,
        text="Выберите из доступных вариантов:",
        reply_markup=admin_menu_markup()
    )


@dp.message_handler(text=inform)
@admin_handlers
async def inform_message(message: types.Message):
    """Вывод отчета."""
    await bot.send_message(
        message.from_user.id,
        "Тут информация о встречах за прошедшую неделю"
    )
