from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Session

engine = create_engine('sqlite:///data/coffee_database.db')
engine.connect()
db_session = Session(bind=engine)

Base = declarative_base()
