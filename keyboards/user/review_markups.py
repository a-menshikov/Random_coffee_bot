from aiogram.types import ReplyKeyboardMarkup

review_answer_1 = "Все было просто замечательно!"
review_answer_2 = "Общение было интересным."
review_answer_3 = "Не очень. Остались негативные впечатления."
review_answer_4 = "Моя пара не пришла на встречу."
skip_message = "👉 Пропустить"


def review_markup():
    """Кнопки с вариантами отзыва о встрече."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(review_answer_1)
    markup.add(review_answer_2)
    markup.add(review_answer_3)
    markup.add(review_answer_4)
    markup.add(skip_message)
    return markup
