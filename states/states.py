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

class ReviewState(StatesGroup):
    start = State()