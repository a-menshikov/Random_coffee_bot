from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date

from base_and_services.db_loader import engine, Base


class Gender(Base):
    __tablename__ = 'genders'
    id = Column(Integer, primary_key=True, unique=True)
    gender_name = Column(String(20), nullable=False, unique=True)


class Users(Base):
    __tablename__ = 'user_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    teleg_id = Column(Integer, nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    birthday = Column(Date(), nullable=True)
    about = Column(String(500), nullable=True)
    gender = Column(Integer, ForeignKey('genders.id'))


class BanList(Base):
    __tablename__ = 'ban_list'
    id = Column(Integer, primary_key=True, autoincrement=True)
    banned_user_id = Column(Integer, ForeignKey('user_info.id'))
    ban_status = Column(Boolean, nullable=False)
    date_of_ban = Column(Date, default=date.today())
    comment_to_ban = Column(String(500), nullable=False)
    date_of_unban = Column(Date, nullable=True, default='null')
    comment_to_unban = Column(String(500), nullable=True, default='null')


class Holidays(Base):
    __tablename__ = 'holidays_status'
    id = Column(Integer, ForeignKey('user_info.id'), primary_key=True)
    status = Column(Boolean, nullable=False, default=0)
    till_date = Column(Date, nullable=True, default='null')


class MetInfo(Base):
    __tablename__ = 'met_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_user_id = Column(Integer, ForeignKey('user_info.id'))
    second_user_id = Column(Integer, ForeignKey('user_info.id'))
    date = Column(Date, default=date.today())


class MetsReviews(Base):
    __tablename__ = 'mets_reviews'
    id = Column(Integer, primary_key=True, autoincrement=True)
    met_id = Column(Integer, ForeignKey('met_info.id'))
    who_id = Column(Integer, ForeignKey('user_info.id'))
    about_whom_id = Column(Integer, ForeignKey('user_info.id'))
    grade = Column(Integer, nullable=False)
    comment = Column(String(500), nullable=True)
    date = Column(Date, default=date.today(), onupdate=date.today())


class UserMets(Base):
    __tablename__ = 'user_mets'
    id = Column(Integer, ForeignKey('user_info.id'), primary_key=True)
    met_info = Column(String(), nullable=False, default='{}')


class UserStatus(Base):
    __tablename__ = 'user_status'
    id = Column(Integer, ForeignKey('user_info.id'), primary_key=True)
    status = Column(Boolean, nullable=False, default=1)


async def create_tables():
    Base.metadata.create_all(engine)
