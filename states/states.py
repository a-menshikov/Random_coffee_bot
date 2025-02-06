from aiogram.dispatcher.filters.state import State, StatesGroup


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
    message_send = State()


class ReviewState(StatesGroup):
    start = State()
    grade = State()
    comment = State()


class BannedState(StatesGroup):
    start = State()
