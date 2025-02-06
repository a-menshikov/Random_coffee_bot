import datetime


def date_from_db_to_message(date):
    date_from_db = datetime.datetime.strptime(date, "%Y-%m-%d")
    date_text = date_from_db.strftime("%d.%m.%Y")
    return date_text


def date_from_message_to_db(date):
    date_from_message = datetime.datetime.strptime(date, "%d.%m.%Y")
    date_text = date_from_message.strftime("%Y-%m-%d")
    return date_text
