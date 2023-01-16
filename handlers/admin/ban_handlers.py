import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.admin.validators import *
from keyboards import *
from loader import *
from states import AdminData


@dp.message_handler(text=ban_list, state=AdminData.start)
async def ban_list(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        "Что вы хотите сделать?",
        reply_markup=admin_ban_markup()
    )


@dp.message_handler(text=add_to_ban_list, state=AdminData.start)
async def ban_list_add(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        "Введите id пользователя, которого необходимо забанить:",
        reply_markup=admin_back_markup()
    )
    await AdminData.user_ban.set()


@dp.message_handler(state=AdminData.user_ban)
async def ban_list_add_answer(message: types.Message, state: FSMContext):
    user_id = message.text
    if not await ban_validator(message):
        return
    await state.update_data(banned_user_id=user_id)
    await comment_to_ban(message)


async def comment_to_ban(message):
    await bot.send_message(
        message.from_user.id,
        "Введите коментарий (длина комментария не менее 10 "
        "и не более 500 символов):",
    )
    await AdminData.comment_to_ban.set()


@dp.message_handler(state=AdminData.comment_to_ban)
async def comment_to_ban_answer(message: types.Message, state: FSMContext):
    comment = message.text
    if not await comment_validator(comment):
        await bot.send_message(
            message.from_user.id,
            "Комментарий должен быть не менее 10 и не более 500 символов"
        )
        return
    data = await state.get_data()
    banned_user_id = data.get('banned_user_id')
    await save_to_ban(banned_user_id, comment)
    await bot.send_message(message.from_user.id,
                           "Пользователь добвлен в бан-лист")
    await back_to_main(message, state)


async def save_to_ban(banned_user_id, comment):
    today = datetime.date.today()
    queries = {
        """INSERT INTO ban_list (banned_user_id, ban_status, 
        date_of_ban, comment_to_ban, date_of_unban, comment_to_unban) 
        VALUES (?, ?, ?, ?, ?, ?)""":
            (banned_user_id, 1, today, comment, 'null', 'null'),
        """UPDATE holidays_status SET status=?, till_date=? WHERE id = ?""":
            (0, "null", banned_user_id),
        """UPDATE user_status SET status=? WHERE id = ? """: (0, banned_user_id)
    }
    for query, values in queries.items():
        db_controller.query(query, values)



@dp.message_handler(text=remove_from_ban_list, state=AdminData.start)
async def ban_list_remove(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        "Введите id пользователя, которого необходимо убрать из бан листа:",
        reply_markup=admin_back_markup()
    )
    await AdminData.user_unban.set()


@dp.message_handler(state=AdminData.user_unban)
async def ban_list_remove_answer(message: types.Message, state: FSMContext):
    user_id = message.text
    if not await unban_validator(message):
        return
    await state.update_data(unbanned_user_id=user_id)
    await comment_to_unban(message)


async def comment_to_unban(message):
    await bot.send_message(
        message.from_user.id,
        "Введите коментарий (длина комментария не менее 10 "
        "и не более 500 символов):",
    )
    await AdminData.comment_to_unban.set()


@dp.message_handler(state=AdminData.comment_to_unban)
async def comment_to_unban_answer(message: types.Message, state: FSMContext):
    comment = message.text
    if not await comment_validator(comment):
        await bot.send_message(
            message.from_user.id,
            "Комментарий должен быть не менее 10 и не более 500 символов"
        )
        return
    data = await state.get_data()
    unbanned_user_id = data.get('unbanned_user_id')
    await save_to_unban(unbanned_user_id, comment)
    await bot.send_message(message.from_user.id,
                           "Пользователь исключен из бан-листа")
    await back_to_main(message, state)


async def save_to_unban(unbanned_user_id, comment):
    today = datetime.date.today()
    queries = {
        """UPDATE ban_list SET ban_status = ?, date_of_unban = ?, 
        comment_to_unban = ? WHERE banned_user_id = ? """:
            (0, today, comment, unbanned_user_id),
        """UPDATE user_status SET status=? WHERE id = ? """:
            (1, unbanned_user_id)
    }
    for query, values in queries.items():
        db_controller.query(query, values)


@dp.message_handler(text=back_to_main, state="*")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.reset_state()
    await bot.send_message(
        message.from_user.id,
        "Вы в главном меню",
        reply_markup=admin_main_markup()
    )
