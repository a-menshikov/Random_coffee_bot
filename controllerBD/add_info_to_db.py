from sqlalchemy import exists

from .db_loader import Session
from .models import Gender

el1 = Gender(id=0, gender_name="Не указано")
el2 = Gender(id=1, gender_name="Женский")
el3 = Gender(id=2, gender_name="Мужской")


def add_gender_info():
    with Session() as db_session:
        if not db_session.query(
            exists().where(Gender.gender_name == "Не указано")
        ).scalar():

            db_session.add_all([el1, el2, el3])
            db_session.commit()
