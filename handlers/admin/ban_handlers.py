import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from controllerBD.db_loader import Session
from controllerBD.models import BanList, Holidays, UserStatus
from handlers.admin.handlers import admin_menu
from handlers.admin.validators import ban_validator, comment_validator, unban_validator
from handlers.decorators import admin_handlers
from keyboards.admin import (
    add_to_ban_list,
    admin_ban_markup,
    admin_cancel_markup,
    back_to_main_markup,
    ban_list,
    cancel,
    remove_from_ban_list,
)
from keyboards.user import back_to_main
from loader import bot, logger
from states import AdminData


# @dp.message_handler(text=cancel, state="*")
async def cancel_message(message: types.Message, state: FSMContext):
    """Отмена"""
    await state.finish()
    await admin_menu(message)


# @dp.message_handler(text=ban_list)
@admin_handlers
async def ban_list_message(message: types.Message):
    """Вывод сообщения с выбором действия по бану."""
    await bot.send_message(
        message.from_user.id, "Что вы хотите сделать?", reply_markup=admin_ban_markup()
    )


# @dp.message_handler(text=add_to_ban_list)
@admin_handlers
async def ban_list_add(message: types.Message):
    """Старт процесса добавления пользователя в бан лист."""
    logger.info("Начало процесса добавления пользователя в бан.")
    await bot.send_message(
        message.from_user.id,
        "Введите id пользователя, которого необходимо забанить:",
        reply_markup=admin_cancel_markup(),
    )
    await AdminData.user_ban.set()


# @dp.message_handler(state=AdminData.user_ban)
async def ban_list_add_answer(message: types.Message, state: FSMContext):
    """Получение ответа от админа и проверка введенного id."""
    logger.info(f"Для добавления в бан введен пользователь " f"с if {message.text}.")
    user_id = message.text
    if not await ban_validator(message):
        return
    await state.update_data(banned_user_id=user_id)
    await comment_to_ban(message)


async def comment_to_ban(message):
    """Запрос на добавление комментария к бану."""
    logger.info("Отправка запроса на добавление комментария к бану.")
    await bot.send_message(
        message.from_user.id,
        "Введите комментарий (длина комментария не менее 10 "
        "и не более 500 символов):",
    )

    await AdminData.comment_to_ban.set()


# @dp.message_handler(state=AdminData.comment_to_ban)
async def comment_to_ban_answer(message: types.Message, state: FSMContext):
    """Получение комментария к бану и отправка в запись."""
    logger.info("Комментарий к бану получен. Валидация")
    comment = message.text
    if not await comment_validator(comment):
        await bot.send_message(
            message.from_user.id,
            "Комментарий должен быть не менее 10 и не более 500 символов",
        )
        return
    data = await state.get_data()
    banned_user_id = data.get("banned_user_id")
    await save_to_ban(banned_user_id, comment)
    await bot.send_message(message.from_user.id, "Пользователь добавлен в бан-лист")
    await back_to_main_message(message, state)


async def save_to_ban(banned_user_id, comment):
    """Запись в БД пользователя с баном."""
    with Session() as db_session:
        db_session.add(
            BanList(
                banned_user_id=banned_user_id,
                ban_status=1,
                comment_to_ban=comment,
                date_of_ban=str(datetime.date.today()),
            )
        )
        db_session.query(Holidays).filter(Holidays.id == banned_user_id).update(
            {"status": 0, "till_date": "null"}
        )
        db_session.query(UserStatus).filter(UserStatus.id == banned_user_id).update(
            {"status": 0}
        )
        db_session.commit()


# @dp.message_handler(text=remove_from_ban_list)
@admin_handlers
async def ban_list_remove(message: types.Message):
    """Запуск процесса удаления пользователя из бана."""
    logger.info("Начало процесса вывода пользователя из бана.")
    await bot.send_message(
        message.from_user.id,
        "Введите id пользователя, которого необходимо убрать из бан листа:",
        reply_markup=admin_cancel_markup(),
    )
    await AdminData.user_unban.set()


# @dp.message_handler(state=AdminData.user_unban)
async def ban_list_remove_answer(message: types.Message, state: FSMContext):
    """Получение ответа с id пользователем для вывода из бана. Валидация."""
    logger.info(f"Для вывода из бана введен пользователь " f"с if {message.text}.")
    user_id = message.text
    if not await unban_validator(message):
        return
    await state.update_data(unbanned_user_id=user_id)
    await comment_to_unban(message)


async def comment_to_unban(message):
    """Запрос комментария к выводу из бана пользователя."""
    logger.info("Отправка запроса на добавление комментария к выводу из бана.")
    await bot.send_message(
        message.from_user.id,
        "Введите комментарий (длина комментария не менее 10 "
        "и не более 500 символов):",
    )
    await AdminData.comment_to_unban.set()


# @dp.message_handler(state=AdminData.comment_to_unban)
async def comment_to_unban_answer(message: types.Message, state: FSMContext):
    """Получение комментария к выводу из бана. Валидация."""
    logger.info("Комментарий к выводу из бана получен. Валидация")
    comment = message.text
    if not await comment_validator(comment):
        await bot.send_message(
            message.from_user.id,
            "Комментарий должен быть не менее 10 и не более 500 символов",
        )
        return
    data = await state.get_data()
    unbanned_user_id = data.get("unbanned_user_id")
    await save_to_unban(unbanned_user_id, comment)
    await bot.send_message(message.from_user.id, "Пользователь исключен из бан-листа")
    await back_to_main_message(message, state)


async def save_to_unban(unbanned_user_id, comment):
    """Сохранение в БД, что пользователь выведен из бана."""
    with Session() as db_session:
        db_session.query(BanList).filter(BanList.banned_user_id == unbanned_user_id).update(
            {
                "ban_status": 0,
                "date_of_unban": datetime.date.today(),
                "comment_to_unban": comment,
            }
        )
        db_session.query(UserStatus).filter(UserStatus.id == unbanned_user_id).update(
            {"status": 1}
        )
        db_session.commit()


# @dp.message_handler(text=back_to_main, state="*")
async def back_to_main_message(message: types.Message, state: FSMContext):
    """Возврат в главное меню."""
    await state.reset_state()
    await bot.send_message(
        message.from_user.id,
        "Вы в главном меню",
        reply_markup=back_to_main_markup(message),
    )


def register_admin_ban_handlers(dp: Dispatcher):
    dp.register_message_handler(cancel_message, text=cancel, state="*")
    dp.register_message_handler(ban_list_message, text=ban_list)
    dp.register_message_handler(ban_list_add, text=add_to_ban_list)
    dp.register_message_handler(ban_list_add_answer, state=AdminData.user_ban)
    dp.register_message_handler(comment_to_ban_answer, state=AdminData.comment_to_ban)
    dp.register_message_handler(ban_list_remove, text=remove_from_ban_list)
    dp.register_message_handler(ban_list_remove_answer, state=AdminData.user_unban)
    dp.register_message_handler(
        comment_to_unban_answer, state=AdminData.comment_to_unban
    )
    dp.register_message_handler(back_to_main_message, text=back_to_main, state="*")
