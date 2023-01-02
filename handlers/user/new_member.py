import sqlite3
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from config.bot_config import bot, dp
from handlers.users_handlers.validators.validators import validate_name, \
    validate_birthday

from states.states import UserData


@dp.callback_query_handler(text="confirm_to_save", state=UserData.gender)
async def confirmation_and_save(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Теперь вы добавлены в нашу БД. И будете участвовать в распределении на следующей неделе.')
    data = await state.get_data()
    date_obj = datetime.strptime(data.get('birthday'), '%d.%m.%Y')
    birthday_for_save = str(date_obj.date())
    gender =
    add_to_db(message.from_user.id, data.get('name'), birthday_for_save, data.get('about'), gender)
    await state.reset_state()

@dp.callback_query_handler(text="change_data", state=UserData.gender)
async def change_data(message: types.Message, state: FSMContext):
    await state.reset_state()
    await add_new_user_to_db(message)


def add_to_db(chat_id, name, birthday):
    """Добавляем нового пользователя в базу."""
    conn = sqlite3.connect('random_coffee.db')
    cur = conn.cursor()
    cur.execute("""insert into users values (?, ?, ?, ?, ?, ?)""", (
        chat_id, name, birthday, 1, 0, 'NULL'
    ))
    conn.commit()


async def add_new_user_to_db(message: types.Message):
    await bot.send_message(message.from_user.id, 'Как вас зовут? (Введите только имя)')
    await UserData.name.set()


async def check_data(tg_id, name, birthday, about, gender):
    await bot.send_message(
        tg_id,
        f"Пожалуйста подтвердите ваши данные:\n"
        f"Имя: {name};\n"
        f"Дата рождения:{birthday};\n"
        f"О себе: {about};\n"
        f"Пол: {gender};",
        reply_markup=keyboard_confirm_to_save
    )


keyboard_confirm_to_save = types.InlineKeyboardMarkup()

confirm_to_save = types.InlineKeyboardButton(
    'Подтвердить',
    callback_data='confirm_to_save'
)
change_data = types.InlineKeyboardButton(
    'Изменить',
    callback_data='change_data'
)
keyboard_confirm_to_save.row(confirm_to_save, change_data)

async def end_registration(state, message):
    data = await state.get_data()
    name = data.get('name')
    birthday = data.get('birthday')
    tg_id = message.from_user.id
    await check_data(tg_id, name, birthday)


@dp.message_handler(state=UserData.name)
async def answer_name(message: types.Message, state: FSMContext):
    """Первое состояние. Сохранение имени в хранилище памяти."""
    name = message.text
    if not validate_name(name):
        await message.answer(f'Что то не так с введенным именем. Имя должно состоять из букв русского или латинского алфавита"')
        return
    await state.update_data(name=name)
    await message.answer(
        "Введите дату Вашего рождения в формате ДД.ММ.ГГГГ")
    await state.set_state(UserData.birthday.state)


@dp.message_handler(state=UserData.birthday)
async def answer_birthday(message: types.Message, state: FSMContext):
    """Второе состояние. Сохранение даты рождения в хранилище памяти."""
    birthday = message.text
    if not await validate_birthday(message):
        return
    await state.update_data(birthday=birthday)
    await state.set_state(UserData.birthday.about)


@dp.message_handler(state=UserData.about)
async def answer_about(message: types.Message, state: FSMContext):
    """Второе состояние. Сохранение даты рождения в хранилище памяти."""
    about = message.text
    if not await validate_about(message):
        return
    await state.update_data(about=about)
    await state.set_state(UserData.birthday.gender)

@dp.message_handler(state=UserData.gender)
async def answer_gender(message: types.Message, state: FSMContext):
    """Второе состояние. Сохранение даты рождения в хранилище памяти."""
    gender = message.text
    if not await validate_gender(message):
        return
    await state.update_data(gender=gender)
    await end_registration(state, message)

