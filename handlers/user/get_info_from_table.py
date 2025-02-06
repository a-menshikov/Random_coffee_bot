from sqlalchemy import exists

from controllerBD.db_loader import Session
from controllerBD.models import Gender, Holidays, Users, UserStatus
from loader import logger


def get_id_from_user_info_table(teleg_id):
    """Получение id пользователя по телеграм id."""
    with Session() as db_session:
        id_obj = db_session.query(Users.id).filter(Users.teleg_id == teleg_id).first()
        return id_obj[0]


def get_teleg_id_from_user_info_table(id):
    """Получение id телеграм чата по id пользователя."""
    with Session() as db_session:
        id_obj = db_session.query(Users.teleg_id).filter(Users.id == id).first()
        return id_obj[0]


async def check_user_in_base(message):
    """Проверяем пользователя на наличие в БД."""
    with Session() as db_session:
        is_exist = db_session.query(
            exists().where(Users.teleg_id == message.from_user.id)
        ).scalar()
        if not is_exist:
            return False
        return True


def get_user_data_from_db(teleg_id):
    """Получение данных пользователя"""
    with Session() as db_session:
        user = db_session.query(Users).filter(Users.teleg_id == teleg_id).first()
        return user.__dict__


def get_user_status_from_db(user_id):
    """Получение статуса участия пользователя из БД"""
    with Session() as db_session:
        user_status = db_session.query(UserStatus).filter(UserStatus.id == user_id).first()
        return user_status.__dict__


def get_holidays_status_from_db(user_id):
    """Получение статуса каникул пользователя из БД"""
    with Session() as db_session:
        holidays = db_session.query(Holidays).filter(Holidays.id == user_id).first()
        return holidays.__dict__


def get_user_info_by_id(user_id):
    """Получение строки информации по id пользователя"""
    with Session() as db_session:
        user = db_session.query(Users).filter(Users.id == user_id).first()
        return user.__dict__


def get_full_user_info_by_id(user_id):
    try:
        with Session() as db_session:
            result = (
                db_session.query(
                    Users.id,
                    Users.teleg_id,
                    Users.name,
                    Users.birthday,
                    Users.about,
                    Gender.gender_name,
                )
                .join(Gender)
                .filter(Users.id == user_id)
                .first()
            )
    except Exception as error:
        logger.error(f"{error}")
        result = None
    finally:
        return result
