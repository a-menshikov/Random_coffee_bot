import sqlite3

from aiogram import types

from config.bot_config import dp, bot
from handlers.user.new_member import add_new_user_to_db


def check_user_in_base(message):
    """Проверяем пользователя на наличие в БД."""
    conn = sqlite3.connect('random_coffee.db')
    cur = conn.cursor()
    info = cur.execute(
        """SELECT * FROM users WHERE tg_id=?""", (message.from_user.id,)
    )
    conn.commit()
    if info.fetchone() is None:
        # Делаем когда нету человека в бд
        return False
    return True

def change_take_part_status_to_yes(message: types.Message):
    conn = sqlite3.connect('random_coffee.db')
    cur = conn.cursor()
    cur.execute("""update users SET take_part = ? where tg_id = ?""", (
        1, message.from_user.id
    ))
    conn.commit()


def change_take_part_status_to_no(message: types.Message):
    conn = sqlite3.connect('random_coffee.db')
    cur = conn.cursor()
    cur.execute("""update users SET take_part = ? where tg_id = ?""", (
        0, message.from_user.id
    ))
    conn.commit()


@dp.callback_query_handler(text="take_part")
async def take_part(message: types.Message):
    if not check_user_in_base(message):
        await bot.send_message(message.from_user.id,
            'Мы не нашли Вас в нашей базе. Пожалуйста ответьте на несколько вопросов и мы добавим Вас в наш список.')
        await add_new_user_to_db(message)
    else:
        change_take_part_status_to_yes(message)
        await bot.send_message(message.from_user.id, 'Ваша заявка принята. Ожидайте распределения')

@dp.callback_query_handler(text="do_not_take_part")
async def do_not_take_part(message: types.Message):
    if not check_user_in_base(message):
        await message.answer(
            'Мы не нашли Вас в нашей базе. Пожалуйста ответьте на несколько вопросов и мы добавим Вас в наш список.')
    change_take_part_status_to_no(message)
    await bot.send_message(message.from_user.id, 'Вы не будете участвовать в распределении на следующей неделе.')

async def question_about_take_part(tg_id):
    await bot.send_message(
        tg_id,
        text=f'Желаешь принять участие на следующей неделе?',
        reply_markup=keyboard_choose_take_part_or_not
    )

keyboard_choose_take_part_or_not = types.InlineKeyboardMarkup()

take_part = types.InlineKeyboardButton(
    'Участвую',
    callback_data='take_part'
)
do_not_take_part = types.InlineKeyboardButton(
    'Не участвую',
    callback_data='do_not_take_part'
)
keyboard_choose_take_part_or_not.row(take_part, do_not_take_part)


def get_data_from_db_for_mailing_list():
    conn = sqlite3.connect('random_coffee.db')

    cur = conn.execute("""SELECT tg_id FROM users where holidays = 0 and take_part = 0""")
    data = cur.fetchall()
    return [element[0] for element in data]

async def get_mailing():
    all_user_for_next_week = get_data_from_db_for_mailing_list()
    print(all_user_for_next_week)
