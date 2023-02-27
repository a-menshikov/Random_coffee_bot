from sqlalchemy import text
from controllerBD.db_loader import db_session
from handlers.user.work_with_date import date_from_db_to_message


def prepare_user_info():
    query = text("""SELECT mr.about_whom_id, ui.teleg_id, ui.name, un.username, 
            bl.ban_status, COUNT(*), MAX(mr.date_of_comment), mr.comment
            FROM mets_reviews as mr 
            LEFT JOIN user_info as ui 
            ON mr.about_whom_id = ui.id
            LEFT JOIN tg_usernames as un 
            ON mr.about_whom_id = un.id
            LEFT JOIN ban_list as bl 
            ON mr.about_whom_id = bl.id
            WHERE mr.grade = 0
            GROUP BY  mr.about_whom_id
            ORDER BY mr.date_of_comment DESC""")

    users = db_session.execute(query)
    return users

def prepare_report_message(users):
    message_list = []
    message = ""
    for user in users:
        if not user[3]:
            username = ""
        else:
            username = f' (@{user[3]})'
        if user[4] == 0:
            status = "Не забанен"
        else:
            status = "Забанен"
        if user[7] == 'null':
            comment = "Комментарий не был добавлен."
        else:
            comment = f"{user[7]}"
        date = date_from_db_to_message(user[6])
        user_message = f'ID пользователя: {user[0]};\n' \
                       f'Ник пользователя: <a href="tg://user?id={user[1]}">' \
                       f'{user[2]}</a>{username}.\n' \
                       f'Статус: {status}.\n' \
                       f'<b>Штрафных балов - {user[5]}</b>\n' \
                       f'{date} Последний комментарий: {comment}'
        if len(message + '\n\n' + user_message) > 4095:
            message_list.append(message)
            message = user_message
        else:
            message = message + '\n\n' + user_message
    message_list.append(message)

    return message_list
