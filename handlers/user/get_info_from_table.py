from loader import db_controller, logger


def get_id_from_user_info_table(teleg_id):
    """Получение id пользователя по телеграм id."""
    query_id = """SELECT id FROM user_info WHERE teleg_id=?"""
    values_id = (teleg_id,)
    id_obj = db_controller.select_query(query_id, values_id)
    return id_obj.fetchone()[0]


def get_teleg_id_from_user_info_table(id):
    """Получение id телеграм чата по id пользователя."""
    query_id = """SELECT teleg_id FROM user_info WHERE id=?"""
    values_id = (id,)
    id_obj = db_controller.select_query(query_id, values_id)
    return id_obj.fetchone()[0]


async def check_user_in_base(message):
    """Проверяем пользователя на наличие в БД."""
    query = """SELECT * FROM user_info WHERE teleg_id=?"""
    values = (message.from_user.id,)
    info = db_controller.select_query(query, values)
    if info.fetchone() is None:
        return False
    return True


def get_user_data_from_db(teleg_id):
    """Получение id пользователя"""
    query = """SELECT * FROM user_info WHERE teleg_id=?"""
    values = (teleg_id,)
    row = db_controller.row_factory(query, values)
    return row.fetchone()


def get_user_status_from_db(user_id):
    """Получение статуса участия пользователя из БД"""
    query = """SELECT * FROM user_status WHERE id=?"""
    values = (user_id,)
    row = db_controller.row_factory(query, values)
    return row.fetchone()


def get_holidays_status_from_db(user_id):
    """Получение статуса каникул пользователя из БД"""
    query = """SELECT * FROM holidays_status WHERE id=?"""
    values = (user_id,)
    row = db_controller.row_factory(query, values)
    return row.fetchone()


def get_user_info_by_id(user_id):
    """Получение строки информации по id пользователя"""
    query = """SELECT * FROM user_info WHERE id=?"""
    values = (user_id,)
    row = db_controller.row_factory(query, values)
    return row.fetchone()


def get_full_user_info_by_id(user_id):
    query = (
        "SELECT u.id, u.teleg_id, "
        "u.name, u.birthday,"
        "u.about, g.gender_name "
        "FROM user_info as u "
        "LEFT JOIN genders g "
        "ON g.id = u.gender "
        "WHERE u.id = ?"
    )
    try:
        result = db_controller.select_query(query, (user_id, )).fetchone()
    except Exception as error:
        logger.error(f"{error}")
        result = None
    finally:
        return result
