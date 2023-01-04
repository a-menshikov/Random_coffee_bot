import sqlite3

from aiogram import types

from data.config import dp, bot

from keyboards.user import *
from handlers.user.new_member import get_gender_from_db, start_registration



@dp.message_handler(text=menu_message)
async def main_menu(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        text="Меню:",
        reply_markup=menu_markup()
    )


@dp.callback_query_handler(text=my_profile_message)
async def send_profile(message: types.Message):
    data = dict(get_user_data_from_db(message.from_user.id))
    if data['about'] == 'null':
        data['about'] = 'Не указано'
    gender_id = data['gender']
    gender_status = get_gender_from_db(gender_id)
    data['gender'] = gender_status
    birthday = data['birthday'].split('-')
    birthday.reverse()
    data['birthday'] = '-'.join(birthday)
    await bot.send_message(
        message.from_user.id,
        f"Имя: {data['name']};\n"
        f"Дата рождения: {data['birthday']};\n"
        f"О себе: {data['about']};\n"
        f"Пол: {data['gender']};",
        reply_markup=edit_profile_markup()
    )

def get_user_data_from_db(teleg_id):
    conn = sqlite3.connect('data/coffee_database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.execute(
        """SELECT * FROM user_info WHERE teleg_id=?""", (teleg_id,)
    )
    row = cur.fetchone()
    return row


@dp.callback_query_handler(text=edit_profile_message)
async def edit_profile(message: types.Message):
    await start_registration(message)

@dp.callback_query_handler(text=about_bot_message)
async def about_bot_message(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        "Тут будет сообщение о боте"
    )
