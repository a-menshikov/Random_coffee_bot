import json
from datetime import date

from sqlalchemy import desc, or_

from data import ADMIN_TG_ID, DEFAULT_PARE_iD
from loader import bot, logger

from .db_loader import Session
from .models import MetInfo, UserMets, Username, Users, UserStatus


async def update_mets(match_info: dict):
    for match in match_info.items():
        try:
            with Session() as db_session:
                if match[0] and match[1]:
                    logger.debug(f"Adding match: {match}")
                    first_user = match[0]
                    second_user = match[1]
                    db_session.add(
                        MetInfo(
                            first_user_id=first_user,
                            second_user_id=second_user,
                            date=str(date.today()),
                        )
                    )
                    db_session.commit()
        except Exception as error:
            logger.error(
                f"Встреча для пользователей {match} " f"не записана. Ошибка - {error}"
            )
            continue


def update_one_user_mets(first_user: int, second_user: int):
    """Записывает в user_mets информацию об одном пользователе."""
    with Session() as db_session:
        first_user_mets = (
            db_session.query(UserMets.met_info).filter(UserMets.id == first_user).first()
        )
        user_mets = json.loads(first_user_mets[0])
        new_met_id = (
            db_session.query(MetInfo.id)
            .filter(
                MetInfo.date == str(date.today()),
                or_(
                    MetInfo.first_user_id == first_user,
                    MetInfo.second_user_id == first_user,
                ),
            )
            .order_by(desc(MetInfo.id))
            .limit(1)
            .first()[0]
        )
        user_mets[new_met_id] = second_user
        new_mets_value = json.dumps(user_mets)
        db_session.query(UserMets).filter(UserMets.id == first_user).update(
            {"met_info": new_mets_value}
        )
        db_session.commit()


def update_all_user_mets(match_info: dict):
    """Записывает в user_mets всю информацию о новых встречах."""
    for match in match_info.items():
        if match[0] and match[1]:
            first_user = match[0]
            second_user = match[1]
            try:
                update_one_user_mets(first_user, second_user)
            except Exception as error:
                logger.error(
                    f"Информация о встречах пользователя "
                    f"{first_user} не обновлена. "
                    f" Ошибка - {error}"
                )
            first_user = match[1]
            second_user = match[0]
            try:
                update_one_user_mets(first_user, second_user)
            except Exception as error:
                logger.error(
                    f"Информация о встречах пользователя "
                    f"{first_user} не обновлена. "
                    f" Ошибка - {error}"
                )
    logger.info("Запись информации о новых встречах завершена")


def get_defaulf_pare_base_id():
    """Получить id дефолтного юзера из базы."""
    with Session() as db_session:
        return (
            db_session.query(Users.id)
            .filter(Users.teleg_id == int(DEFAULT_PARE_iD))
            .first()[0]
        )


def get_user_count_from_db():
    with Session() as db_session:
        all_users = db_session.query(Users).count()
        active_users = db_session.query(UserStatus).filter(UserStatus.status == 1).count()
        return {"all_users": all_users, "active_users": active_users}

def get_active_user_names_from_db():
    users = []
    with Session() as db_session:
        for active_user_id in [user.id for user in db_session.query(UserStatus).filter(UserStatus.status == 1).all()]:
            user_tg_username = db_session.query(Username).filter(Username.id == active_user_id).one_or_none().username
            user_name = db_session.query(Users).filter(Users.id == active_user_id).one_or_none().name
            users.append({"name": user_name, "tg_username": user_tg_username})
        return users

def get_user_id_from_db(teleg_id: int) -> int:
    """Получает id юзера в базе по телеграм id"""
    with Session() as db_session:
        return db_session.query(Users.id).filter(Users.teleg_id == teleg_id).first()[0]


def get_tg_username_from_db_by_teleg_id(teleg_id: int) -> int:
    """Получает телеграм-юзернейм по telegram id"""
    with Session() as db_session:
        base_id = get_user_id_from_db(teleg_id)
        answer = db_session.query(Username.username).filter(Username.id == base_id).first()
        if answer:
            return answer[0]
        return None


def get_tg_username_from_db_by_base_id(base_id: int) -> int:
    """Получает телеграм-юзернейм по id в базе"""
    with Session() as db_session:
        answer = db_session.query(Username.username).filter(Username.id == base_id).first()
        if answer:
            return answer[0]
        return None


async def send_message_to_admins(message):
    """Отправляет сообщение списку админов."""
    for i in list(map(int, ADMIN_TG_ID.split())):
        try:
            await bot.send_message(i, message)
        except Exception as error:
            logger.error(f"Сообщение {message} не ушло админу {i}. {error}")
