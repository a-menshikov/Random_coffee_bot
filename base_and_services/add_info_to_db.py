from sqlalchemy import exists

from base_and_services.db_loader import db_session
from base_and_services.models import Gender, MetInfo

el1 = Gender(id=0, gender_name="Не указано")
el2 = Gender(id=1, gender_name="Женский")
el3 = Gender(id=2, gender_name="Мужской")

if not db_session.query(exists().where(Gender.gender_name == 'Не указано')).scalar():
    db_session.add_all([el1, el2, el3])
    db_session.commit()
