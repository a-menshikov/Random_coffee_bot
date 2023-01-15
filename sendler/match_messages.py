from aiogram import Bot

from keyboards import help_texts_markup
from loader import db_controller, logger

from data import ADMIN_TG_ID


async def send_match_messages(match_info: dict, bot: Bot):
    """Рассылка сообщений после распределения пар на неделю."""
    for match in match_info.items():
        users_info = pare_users_query(match)
        if not users_info:
            logger.error(f'Не удалось получить информацию '
                         f'из БД для пары {match}')
            continue
        elif len(users_info) == 2:
            first_user = users_info[0]
            first_user_id = first_user[1]
            second_user = users_info[1]
            second_user_id = second_user[1]
            try:
                first_message = make_message(first_user)
            except Exception as error:
                logger.error(f'Не удалось сформировать сообщение о '
                             f'пользователе {first_user}. Ошибка {error}')
            try:
                second_message = make_message(second_user)
            except Exception as error:
                logger.error(f'Не удалось сформировать сообщение о '
                             f'пользователе {second_user}. Ошибка {error}')
            try:
                await bot.send_message(second_user_id, first_message,
                                       parse_mode="HTML",
                                       reply_markup=help_texts_markup())
                logger.info(f'Сообщение для пользователя {second_user_id} '
                            f'отправлено')
            except Exception as error:
                logger.error(f'Сообщение для пользователя {second_user_id} '
                             f'не отправлено. Ошибка {error}')
            try:
                await bot.send_message(first_user_id, second_message,
                                       parse_mode="HTML",
                                       reply_markup=help_texts_markup())
                logger.info(f'Сообщение для пользователя {first_user_id} '
                            f'отправлено')
            except Exception as error:
                logger.error(f'Сообщение для пользователя {first_user_id} '
                             f'не отправлено. Ошибка {error}')
        else:
            fail_user = users_info[0]
            fail_user_id = fail_user[1]
            fail_user_db_id = fail_user[0]
            message = make_message(fail_user, fail=True)
            try:
                await bot.send_message(ADMIN_TG_ID,
                                       message, parse_mode="HTML")
                logger.info(f'Сообщение админу об отсутствии пары '
                            f'для пользователя {fail_user_db_id} '
                            f'отправлено')
            except Exception as error:
                logger.error(f'Сообщение админу об отсутствии пары '
                             f'для пользователя {fail_user_db_id} '
                             f'не отправлено. Ошибка {error}')


def make_message(user_info: tuple, fail: bool = False):
    """Формирует строку для отправки."""
    if not fail:
        user_id = user_info[1]
        user_name = user_info[2]
        user_birthday = user_info[3]
        user_about = user_info[4]
        user_gender = user_info[5]
        message = (f'На этой неделе Ваша пара для кофе: '
                   f'<a href="tg://user?id={user_id}">{user_name}</a>\n'
                   f'Дата рождения: {user_birthday}\n'
                   f'Информация: {user_about}\n'
                   f'Пол: {user_gender}\n')
    else:
        fail_user_id = user_info[1]
        fail_user_name = user_info[2]
        message = (f'Без пары на этой неделе: <a href="tg://user?id'
                   f'={fail_user_id}">{fail_user_name}</a>')
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
    try:
        result = db_controller.select_query(query, pare).fetchall()
    except Exception:
        result = None
    finally:
        return result
