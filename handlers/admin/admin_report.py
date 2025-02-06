from sqlalchemy import text

from controllerBD.db_loader import Session
from handlers.user.work_with_date import date_from_db_to_message


def prepare_user_info():
    """Формируем список пользователей со штрафными баллами и другой инф."""
    with Session() as db_session:
        query = text(
            """SELECT 
                mr.about_whom_id, 
                ui.teleg_id, 
                ui.name, 
                un.username, 
                COUNT(
                    CASE
                        WHEN mr.grade = 0 THEN 1
                        ELSE NULL
                    END
                ) AS cnt_fail, 
                MAX(mr.date_of_comment) AS last_comment, 
                mr.comment,
                bl.ban_status
            FROM mets_reviews AS mr
            LEFT JOIN user_info AS ui 
                ON mr.about_whom_id = ui.id
            LEFT JOIN tg_usernames AS un 
                ON mr.about_whom_id = un.id
            LEFT JOIN (
                SELECT 
                    banned_user_id, 
                    MAX(id) AS max_id, 
                    ban_status
                FROM ban_list
                GROUP BY banned_user_id, ban_status
            ) AS bl 
                ON mr.about_whom_id = bl.banned_user_id
            WHERE mr.grade = 0
            GROUP BY 
                mr.about_whom_id, 
                ui.teleg_id, 
                ui.name, 
                un.username, 
                mr.comment, 
                bl.ban_status
            ORDER BY MAX(mr.date_of_comment) DESC;
            """
        )

        users = db_session.execute(query)
        return users


def prepare_report_message(users):
    """Подготовка списка сообщений для отправки."""
    message_list = []
    message = ""
    for user in users:
        if not user[3]:
            username = ""
        else:
            username = f" (@{user[3]})"
        if user[7] == 0 or user[7] is None:
            status = "Не забанен"
        else:
            status = "Забанен"
        if user[6] == "null":
            comment = "Комментарий не был добавлен."
        else:
            comment = f"{user[6]}"
        date = date_from_db_to_message(user[5])
        user_message = (
            f"ID пользователя: {user[0]};\n"
            f'Ник пользователя: <a href="tg://user?id={user[1]}">'
            f"{user[2]}</a>{username}.\n"
            f"Статус: {status}.\n"
            f"<b>Штрафных балов - {user[4]}</b>\n"
            f"{date} Последний комментарий: {comment}"
        )
        if len(message + "\n\n" + user_message) > 4095:
            message_list.append(message)
            message = user_message
        else:
            message = message + "\n\n" + user_message
    message_list.append(message)

    return message_list
