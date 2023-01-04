import sqlite3

from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import dp, bot
from handlers.user.validators import *

from states.states import UserData
from keyboards.user import *

def get_gender_from_db(status):
    conn = sqlite3.connect('data/coffee_database.db')
    cur = conn.cursor()
    info = cur.execute(
        """SELECT gender_name FROM genders WHERE id=?""", (status,)
    )
    return info.fetchone()[0]

async def check_user_in_base(message):
    """Проверяем пользователя на наличие в БД."""
    conn = sqlite3.connect('data/coffee_database.db')
    cur = conn.cursor()
    info = cur.execute(
        """SELECT * FROM user_info WHERE teleg_id=?""", (message.from_user.id,)
    )
    if info.fetchone() is None:
        # Делаем когда нету человека в бд
        return False
    return True

@dp.message_handler(state=UserData.check_info)
async def confirmation_and_save(message: types.Message, state: FSMContext):
    if not await validate_check_info(message):
        return
    answer = message.text
    if answer == back_message:
        await question_gender(message)
    else:
        await bot.send_message(
            message.from_user.id,
            'Теперь вы добавлены в нашу БД. И будете участвовать в распределении на следующей неделе.',
            reply_markup=ReplyKeyboardRemove()
        )
        await bot.send_message(
            message.from_user.id,
            text="Нажмите кнопку меню и выберите из доступных вариантов",
            reply_markup=main_markup(),
        )
        data = await state.get_data()
        date_obj = datetime.strptime(data.get('birthday'), '%d.%m.%Y')
        birthday_for_save = str(date_obj.date())
        if await check_user_in_base(message):
            update_profile_db(message.from_user.id, data.get('name'), birthday_for_save, data.get('about'), data.get('gender'))
        else:
            add_to_db(message.from_user.id, data.get('name'), birthday_for_save, data.get('about'), data.get('gender'))
            add_new_user_in_status_table(message.from_user.id)
        await state.reset_state()

async def change_data(message: types.Message, state: FSMContext):
    await state.reset_state()
    await start_registration(message)




def add_to_db(chat_id, name, birthday, about, gender):
    """Добавляем нового пользователя в базу."""
    conn = sqlite3.connect('data/coffee_database.db')
    cur = conn.cursor()
    cur.execute("""insert into user_info (teleg_id, name, birthday, about, gender) values (
    ?,?,?,?,?)""", (
        chat_id, name, birthday, about, gender
    ))
    conn.commit()

def update_profile_db(teleg_id, name, birthday, about, gender):
    conn = sqlite3.connect('data/coffee_database.db')
    cur = conn.cursor()
    cur.execute("""UPDATE user_info SET name = ?, birthday = ?, about = ?, gender =? WHERE teleg_id = ? """, (
        name, birthday, about, gender, teleg_id
    ))
    conn.commit()

def add_new_user_in_status_table(teleg_id):
    """Добавляем нового пользователя в базу."""
    conn = sqlite3.connect('data/coffee_database.db')
    cur = conn.cursor()
    id_obj = cur.execute(
        """SELECT id FROM user_info WHERE teleg_id=?""", (teleg_id,)
    )
    teleg_id = id_obj.fetchone()[0]
    cur.execute("""insert into user_status (id, status) values (
    ?,?)""", (
        teleg_id, 1
    ))
    cur.execute("""insert into holidays_status (id, status, till_date) values (
        ?,?,?)""", (
        teleg_id,
        0,
        'null'
    ))
    conn.commit()


@dp.message_handler(text="Регистрация", state=UserData.start)
async def start_registration(message: types.Message):
    """Первое состояние. Старт регистрации."""
    await bot.send_message(
        message.from_user.id,
        'Как вас зовут? (Введите только имя)',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await UserData.name.set()

async def check_data(tg_id, name, birthday, about, gender):
    await bot.send_message(
        tg_id,
        f"Пожалуйста подтвердите ваши данные:\n"
        f"Имя: {name};\n"
        f"Дата рождения:{birthday};\n"
        f"О себе: {about};\n"
        f"Пол: {gender};",
        reply_markup=confirm_markup()
    )
    await UserData.check_info.set()

async def end_registration(state, message):
    data = await state.get_data()
    name = data.get('name')
    birthday = data.get('birthday')
    about = data.get('about')
    if about == 'null':
        about = 'Не указано'
    gender = get_gender_from_db(data.get('gender'))
    tg_id = message.from_user.id
    await check_data(tg_id, name, birthday, about, gender)


@dp.message_handler(state=UserData.name)
async def answer_name(message: types.Message, state: FSMContext):
    """Второе состояние. Сохранение имени в хранилище памяти."""
    name = message.text
    if not validate_name(name):
        await message.answer(f'Что то не так с введенным именем. Имя должно состоять из букв русского или латинского алфавита"')
        return
    await state.update_data(name=name)
    await question_birthday(message)

async def question_birthday(message: types.Message):
    """Запрос даты рождения"""
    await bot.send_message(
        message.from_user.id,
        'Введите дату рождения в формате ДД.ММ.ГГГГ',
        reply_markup=register_reply_markup()
    )
    await UserData.birthday.set()



@dp.message_handler(state=UserData.birthday)
async def answer_birthday(message: types.Message, state: FSMContext):
    """Третье состояние. Сохранение даты рождения в хранилище памяти."""
    birthday = message.text
    if birthday == back_message:
        await start_registration(message)
    else:
        if not await validate_birthday(message):
            return
        await state.update_data(birthday=birthday)
        await question_about(message)

async def question_about(message: types.Message):
    """Запрос информации о пользователе"""
    await bot.send_message(
        message.from_user.id,
        "Введите немного информации о себе",
        reply_markup=register_can_skip_reply_markup()
    )
    await UserData.about.set()

@dp.message_handler(state=UserData.about)
async def answer_about(message: types.Message, state: FSMContext):
    """Четвертое состояние. Сохранение информации о пользователе в хранилище памяти."""
    about = message.text
    if about == back_message:
        await question_birthday(message)
    elif about == skip_message:
        about = 'null'
    else:
        if not await validate_about(about):
            return
    await state.update_data(about=about)
    await question_gender(message)


async def question_gender(message: types.Message):
    """Запрос пола пользователя"""
    await bot.send_message(
        message.from_user.id,
        "Выберите пол",
        reply_markup=register_man_or_woman_markup()
    )
    await UserData.gender.set()


@dp.message_handler(state=UserData.gender)
async def answer_gender(message: types.Message, state: FSMContext):
    """Пятое состояние. Сохранение гендера в хранилище памяти."""
    gender = message.text
    if gender == back_message:
        await question_about(message)
    if not await validate_gender(message):
        return
    elif gender == skip_message:
        gender = 0
    elif gender == woman_message:
        gender = 1
    elif gender == man_message:
        gender = 2
    await state.update_data(gender=gender)
    await end_registration(state, message)

