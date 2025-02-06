from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .db_loader import Base, engine


class Gender(Base):
    __tablename__ = "genders"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    gender_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)


class Users(Base):
    __tablename__ = "user_info"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teleg_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    birthday: Mapped[str]
    about: Mapped[str] = mapped_column(String(500), nullable=False)
    gender: Mapped[int] = mapped_column(Integer, ForeignKey("genders.id"))


class BanList(Base):
    __tablename__ = "ban_list"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    banned_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_info.id"))
    ban_status: Mapped[int] = mapped_column(Integer, default=1)
    date_of_ban: Mapped[str] = mapped_column(default="null")
    comment_to_ban: Mapped[str] = mapped_column(String(500))
    date_of_unban: Mapped[str] = mapped_column(default="null")
    comment_to_unban: Mapped[str] = mapped_column(String(500), default="null")


class Holidays(Base):
    __tablename__ = "holidays_status"
    id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_info.id"), primary_key=True
    )
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    till_date: Mapped[str] = mapped_column(String, nullable=False, default="null")


class MetInfo(Base):
    __tablename__ = "met_info"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_user_id: Mapped[int] = mapped_column(ForeignKey("user_info.id"))
    second_user_id: Mapped[int] = mapped_column(ForeignKey("user_info.id"))
    date: Mapped[str]


class MetsReview(Base):
    __tablename__ = "mets_reviews"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    met_id: Mapped[int] = mapped_column(ForeignKey("met_info.id"))
    who_id: Mapped[int] = mapped_column(ForeignKey("user_info.id"))
    about_whom_id: Mapped[int] = mapped_column(ForeignKey("user_info.id"))
    grade: Mapped[int]
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    date_of_comment: Mapped[str]


class UserMets(Base):
    __tablename__ = "user_mets"
    id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_info.id"), primary_key=True
    )
    met_info: Mapped[str] = mapped_column(nullable=False, default="{}")


class UserStatus(Base):
    __tablename__ = "user_status"
    id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_info.id"), primary_key=True
    )
    status: Mapped[int] = mapped_column(default=1)


class Username(Base):
    __tablename__ = "tg_usernames"
    id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_info.id"), primary_key=True
    )
    username: Mapped[str]


def create_tables():
    Base.metadata.create_all(engine)
