from aiogram.dispatcher.filters.state import StatesGroup, State


class UserData(StatesGroup):
    """Машина состояний пользователя"""
    start = State()
    name = State()
    birthday = State()
    about = State()
    gender = State()
    end_registration = State()
    check_info = State()


class AdminData(StatesGroup):
    """Машина состояний админа"""
    start = State()
    user_ban = State()
    comment_to_ban = State()
    user_unban = State()
    comment_to_unban = State()


class ReviewState(StatesGroup):
    start = State()


class BannedState(StatesGroup):
    start = State()
