from sqlalchemy import Integer, Column, ForeignKey, Text
from datetime import date

from .db_loader import engine, Base


class Gender(Base):
    __tablename__ = 'genders'
    id = Column(Integer, primary_key=True, unique=True)
    gender_name = Column(Text(100), nullable=False, unique=True)


class Users(Base):
    __tablename__ = 'user_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    teleg_id = Column(Integer, nullable=False, unique=True)
    name = Column(Text(100), nullable=False)
    birthday = Column(Text(), nullable=False)
    about = Column(Text(500), nullable=False)
    gender = Column(Integer, ForeignKey('genders.id'))


class BanList(Base):
    __tablename__ = 'ban_list'
    id = Column(Integer, primary_key=True, autoincrement=True)
    banned_user_id = Column(Integer, ForeignKey('user_info.id'))
    ban_status = Column(Integer, nullable=False, default=1)
    date_of_ban = Column(Text(), default=str(date.today()))
    comment_to_ban = Column(Text(500), nullable=False)
    date_of_unban = Column(Text(), nullable=False, default='null')
    comment_to_unban = Column(Text(500), nullable=False, default='null')


class Holidays(Base):
    __tablename__ = 'holidays_status'
    id = Column(Integer, ForeignKey('user_info.id'), primary_key=True)
    status = Column(Integer, nullable=False, default=0)
    till_date = Column(Text, nullable=False, default='null')


class MetInfo(Base):
    __tablename__ = 'met_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_user_id = Column(Integer, ForeignKey('user_info.id'))
    second_user_id = Column(Integer, ForeignKey('user_info.id'))
    date = Column(Text(), default=str(date.today()))


class MetsReview(Base):
    __tablename__ = 'mets_reviews'
    id = Column(Integer, primary_key=True, autoincrement=True)
    met_id = Column(Integer, ForeignKey('met_info.id'))
    who_id = Column(Integer, ForeignKey('user_info.id'))
    about_whom_id = Column(Integer, ForeignKey('user_info.id'))
    grade = Column(Integer, nullable=False)
    comment = Column(Text(500), nullable=True)
    date_of_comment = Column(Text(), default=str(date.today()),
                             onupdate=str(date.today()))


class UserMets(Base):
    __tablename__ = 'user_mets'
    id = Column(Integer, ForeignKey('user_info.id'), primary_key=True)
    met_info = Column(Text(), nullable=False, default='{}')


class UserStatus(Base):
    __tablename__ = 'user_status'
    id = Column(Integer, ForeignKey('user_info.id'), primary_key=True)
    status = Column(Integer, nullable=False, default=1)


def create_tables():
    Base.metadata.create_all(engine)
