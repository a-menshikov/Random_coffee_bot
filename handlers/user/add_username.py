from aiogram import types
from sqlalchemy import and_, exists

from controllerBD.db_loader import Session
from controllerBD.models import Username
from handlers.user.get_info_from_table import get_id_from_user_info_table
from loader import logger


async def check_username(message: types.Message):
    with Session() as db_session:
        user_id = get_id_from_user_info_table(message.from_user.id)
        username = message.from_user.username
        is_exist = db_session.query(exists().where(Username.id == user_id)).scalar()
        if not is_exist:
            db_session.add(Username(id=user_id, username=username))
            db_session.commit()
            logger.info(f"В базу добавлен Username пользователя {user_id}")
        elif not db_session.query(
            exists().where(and_(Username.id == user_id, Username.username == username))
        ).scalar():
            db_session.query(Username).filter(Username.id == user_id).update(
                {"username": username}
            )
            db_session.commit()
            logger.info(f"Обновлен Username пользователя {user_id}")
        else:
            pass
