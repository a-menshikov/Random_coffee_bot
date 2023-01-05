from importlib.machinery import SourceFileLoader

from aiogram import Bot

clas = SourceFileLoader("module.name", "./controllerBD/manage_db.py").load_module()
clas_1 = SourceFileLoader("module.name", "./data/__init__.py").load_module()

ADMIN_TG_ID = clas_1.ADMIN_TG_ID


async def send_match_messages(match_info: dict, bot: Bot):
    """Рассылка сообщений после распределения пар на неделю."""
    for match in match_info.items():
        users_info = pare_users_query(match)
        if len(users_info) == 2:
            first_user = users_info[0]
            first_user_id = first_user[1]
            second_user = users_info[1]
            second_user_id = second_user[1]
            first_message = make_message(first_user)
            second_message = make_message(second_user)
            try:
                await bot.send_message(second_user_id, first_message,
                                       parse_mode="HTML")
            except Exception:
                pass  # TODO сюда добавить логгер
            try:
                await bot.send_message(first_user_id, second_message,
                                       parse_mode="HTML")
            except Exception:
                pass  # TODO сюда добавить логгер
        else:
            fail_user = users_info[0]
            fail_user_id = fail_user[1]
            fail_user_name = fail_user[2]
            message = (f'Без пары на этой неделе: <a href="tg://user?id'
                       f'={fail_user_id}">{fail_user_name}</a>')
            try:
                await bot.send_message(ADMIN_TG_ID,
                                       message, parse_mode="HTML")
            except Exception:
                pass  # TODO сюда добавить логгер


def make_message(user_info: tuple):
    """Формирует строку для отправки."""
    user_id = user_info[1]
    user_name = user_info[2]
    user_birthday = user_info[3]
    user_about = user_info[4]
    user_gender = user_info[5]
    message = (f'На этой неделе Ваша пара для кофе: '
               f'<a href="tg://user?id={user_id}">{user_name}</a> \n'
               f'Дата рождения: {user_birthday}\n'
               f'Информация: {user_about}\n'
               f'Пол: {user_gender}\n')
    return message


def pare_users_query(pare: tuple):
    """Запрашивает информацию по паре юзеров из базы."""
    query = (
        "SELECT u.id, u.teleg_id, "
        "u.name, u.birthday,"
        "u.about, g.gender_name "
        "FROM user_info as u "
        "LEFT JOIN genders g "
        "ON g.id = u.gender "
        "WHERE u.id in (?, ?)"
    )
    path = '../data/coffee_database.db'
    db_controller = clas.DatabaseManager(path)
    try:
        result = db_controller.select_query(query, pare).fetchall()
    except Exception:
        result = None  # TODO сюда добавить логгер
    finally:
        return result
