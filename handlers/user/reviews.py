from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.decorators import admin_handlers
from handlers.user.get_info_from_table import \
    get_teleg_id_from_user_info_table, \
    get_id_from_user_info_table
from handlers.user.validators import validate_review_yes_or_no, validate_about, \
    validate_review_grade
from keyboards.admin import review_messages
from keyboards.user import skip_message, menu_markup, \
    review_yes_or_no, no_button, yes_button, review_skip
from loader import bot, db_controller, dp, logger
from states import ReviewState


@dp.message_handler(text=review_messages)
@admin_handlers
async def start_review(message: types.Message):
    """Запускаем процесс сбора отзывов."""
    logger.info("Подготавливаем список ID для запроса отзыва.")
    users_id = set(preparing_list_of_users_id())
    if len(users_id) > 0:
        await request_review(users_id)
    else:
        await bot.send_message(message.from_user.id,
                               "На этой неделе не было встреч.")


async def request_review(users_id):
    """Отправка сообщений запросов по прошедшей встрече."""
    logger.info("Начинаем процесс рассылки сообщений для отзыва")
    for user_id in users_id:
        user_teleg_id = get_teleg_id_from_user_info_table(user_id)
        try:
            await bot.send_message(
                user_teleg_id,
                "Состоялась ли Ваша встреча?",
                reply_markup=review_yes_or_no()
            )
            await ReviewState.start.set()
            logger.info(f"Соообщение пользователю {user_teleg_id} "
                        f"для оценки встречи отправлено.")
        except Exception as error:
            logger.error(f"Сообщение пользователю c {user_teleg_id} "
                         f"не доставлено. {error}")
            continue
    logger.info("Все сообщения разосланы")


@dp.message_handler(state=ReviewState.start)
async def review_answer_yes_or_now(message: types.Message,
                                   state: FSMContext):
    answer = message.text
    if not await validate_review_yes_or_no(message):
        return
    if answer == skip_message:
        await bot.send_message(
            message.from_user.id,
            "В течении 3-х недель после распределения вы можете оставить отзыв "
            "перейдя из главного меню.",
            reply_markup=menu_markup(message)
        )
        await state.reset_state()
    elif answer == no_button:
        await state.update_data(grade=0)
        await question_comment(message)
    elif answer == yes_button:
        await question_grade(message)


async def question_comment(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        "Пожалуйста введите ваш комментарий к отзыву (не более 500 символов).",
        reply_markup=review_skip()
    )
    await ReviewState.comment.set()


@dp.message_handler(state=ReviewState.comment)
async def answer_review_comment(message: types.Message, state: FSMContext):
    if not await validate_about(message):
        return
    answer = message.text
    if answer == skip_message:
        answer = "null"
    await state.update_data(comment=answer)
    user_id = get_id_from_user_info_table(message.from_user.id)
    await state.update_data(user_id=user_id)
    met_id = get_met_id_with_user_last_week(user_id)[0]
    await state.update_data(met_id=met_id)
    await save_or_update_review(message, state)


async def question_grade(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        "Оцените встречу от 1 до 5, где \n"
        "    - 1 - Совсем не понравилась,\n"
        "    - 5 - Все было Супер.",
        reply_markup=review_skip()
    )
    await ReviewState.grade.set()


@dp.message_handler(state=ReviewState.grade)
async def answer_review_grade(message: types.Message, state: FSMContext):
    grade = message.text
    if grade == skip_message:
        await bot.send_message(
            message.from_user.id,
            "В течении 3-х недель вы можете оставить отзыв "
            "перейдя из главного меню.",
            reply_markup=menu_markup(message)
        )
        await state.reset_state()
    elif not await validate_review_grade(grade):
        await bot.send_message(message.from_user.id, "Введите оценку от 1 до 5")
        return
    else:
        await state.update_data(grade=grade)
        await question_comment(message)


def preparing_list_of_users_id():
    """Выгрузка списка ID пользователей из
    таблицы проведенных встреч за неделю."""
    query = """SELECT first_user_id, second_user_id 
    FROM met_info 
    WHERE date
    BETWEEN date('now', '-7 days') AND date('now')"""
    data = db_controller.select_query(query).fetchall()
    logger.info("Список ID для рассылки на отзывы сформирован")
    return [element[0] for element in data] + [element[1] for element in data]


async def save_or_update_review(message, state):
    """Сохранние комментария в БД."""
    data = await state.get_data()
    user_id = data.get('user_id')
    met_id = data.get('met_id')
    grade = data.get('grade')
    comment = data.get('comment')
    if await check_comment_in_bd(user_id, met_id):
        update_review(user_id, met_id, grade, comment)
    else:
        add_review(user_id, met_id, grade, comment)
    await state.reset_state()
    await bot.send_message(
        message.from_user.id,
        "Спасибо за ваш отзыв.",
        reply_markup=menu_markup(message)
    )


def get_met_id_with_user_last_week(user_id):
    """Получение id встречи по пользователю за прошедшую неделю."""
    query = """SELECT id 
        FROM met_info 
        WHERE date
        BETWEEN date('now', '-7 days') AND date('now')
        AND (first_user_id = ? OR second_user_id = ?)
        ORDER BY id DESC
        LIMIT 1"""
    values = (user_id, user_id)
    met_id = db_controller.select_query(query, values).fetchone()
    return met_id

async def check_comment_in_bd(user_id, met_id):
    query = """SELECT * FROM mets_reviews WHERE met_id=? AND who_id =?"""
    values = (met_id, user_id)
    info = db_controller.select_query(query, values)
    if info.fetchone() is None:
        return False
    return True


def update_review(user_id, met_id, grade, comment):
    query = """UPDATE mets_reviews 
            SET grade = ?, comment = ?, date_of_comment = date('now') 
            WHERE met_id = ? AND who_id = ?"""
    values = (grade, comment, met_id, user_id)
    db_controller.query(query, values)
    logger.info(f"Пользователь с ID {user_id} "
                f"обновил комментарий о встрече {met_id}")


def add_review(user_id, met_id, grade, comment):
    query = """SELECT first_user_id, second_user_id
                    FROM met_info 
                    WHERE id = ?"""
    values = (met_id, )
    users = db_controller.row_factory(query, values).fetchone()
    if users['first_user_id'] == user_id:
        about_whom_id = users['second_user_id']
    else:
        about_whom_id = users['first_user_id']
    query = """INSERT INTO mets_reviews (met_id, who_id, about_whom_id,
        grade, comment, date_of_comment) VALUES (?,?,?,?,?, date('now'))"""
    values = (met_id, user_id, about_whom_id, grade, comment)
    db_controller.query(query, values)
    logger.info(f"Пользователь с ID {user_id} "
                f"добавил комментарий о встрече {met_id}")

def get_met_id_with_user_last_three(user_id):
    """Получение id встречи по пользователю за прошедшую неделю."""
    query = """SELECT id 
        FROM met_info 
        WHERE date
        BETWEEN date('now', '-27 days') AND date('now')
        AND (first_user_id = ? OR second_user_id = ?)
        ORDER BY id DESC
        LIMIT 3"""
    values = (user_id, user_id)
    mets_id = db_controller.select_query(query, values).fetchall()
    return [met_id[0] for met_id in mets_id]

@dp.message_handler(text='Пример')
@admin_handlers
async def example(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        """
№ встречи   |   С кем   |   Распределение
__________________________________________
    13  |   Петр    |   23.01.2023
__________________________________________
    14  |   Иванdsdsvvxvxvxcvsdsdfsdfxcv    |   30.01.2023
__________________________________________
        """
    )
