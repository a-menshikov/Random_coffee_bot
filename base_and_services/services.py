import json
from datetime import date

from sqlalchemy import or_, desc, exists

from base_and_services.db_loader import db_session
from base_and_services.models import MetInfo, UserMets, Users, UserStatus
from data import DEFAULT_PARE_iD
from loader import logger


async def update_mets(match_info: dict):
    for match in match_info.items():
        try:
            if all(match):
                first_user = match[0]
                second_user = match[1]
                db_session.add(MetInfo(first_user_id=first_user,
                                       second_user_id=second_user))
        except Exception as error:
            logger.error(f'Встреча для пользователей {match} '
                              f'не записана. Ошибка - {error}')
            continue


def update_one_user_mets(first_user: int, second_user: int):
    """Записывает в user_mets информацию об одном пользователе."""
    first_user_mets = db_session.query(UserMets.met_info).filter(
        UserMets.id == first_user
    ).one()
    user_mets = json.loads(first_user_mets[0])
    new_met_id = db_session.query(MetInfo.id).filter(
        MetInfo.date == date.today(),
        or_(
            MetInfo.first_user_id == first_user,
            MetInfo.second_user_id == first_user
        )).order_by(desc(MetInfo.id)).limit(1).one()[0]
    user_mets[new_met_id] = second_user
    new_mets_value = json.dumps(user_mets)
    db_session.query(UserMets).filter(UserMets.id == first_user). \
        update({'met_info': new_mets_value})
    db_session.commit()


def update_all_user_mets(match_info: dict):
    """Записывает в user_mets всю информацию о новых встречaх."""
    for match in match_info.items():
        if all(match):
            first_user = match[0]
            second_user = match[1]
            try:
                update_one_user_mets(first_user, second_user)
            except Exception as error:
                logger.error(f'Информация о встречах пользователя '
                                  f'{first_user} не обновлена. '
                                  f' Ошибка - {error}')
            first_user = match[1]
            second_user = match[0]
            try:
                update_one_user_mets(first_user, second_user)
            except Exception as error:
                logger.error(f'Информация о встречах пользователя '
                                  f'{first_user} не обновлена. '
                                  f' Ошибка - {error}')
    logger.info('Запись информации о новых встречах завершена')

def get_defaulf_pare_base_id():
    """Получить id дефолтного юзера из базы."""
    return db_session.query(Users.id).filter(
        Users.teleg_id == int(DEFAULT_PARE_iD)
    ).one()[0]


def get_user_count_from_db():
    all_users = db_session.query(Users).count()
    active_users = db_session.query(UserStatus).filter(
        UserStatus.status == 1
    ).count()
    return {"all_users": all_users, "active_users": active_users}


