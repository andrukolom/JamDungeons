import os

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class TelegramStorage:
    users = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "users.sqlite3")
    base_url = 'http://127.0.0.1:8000/api'
    api_auth = ''
    menu_buttons = InlineKeyboardBuilder()
    menu_buttons.add(InlineKeyboardButton(text="Найти квест", callback_data="find_quest"),
                     InlineKeyboardButton(text="Найти квест по id", callback_data="find_quest_by_id"),
                     InlineKeyboardButton(text="Мои прохождения", callback_data="my_passing"),
                     InlineKeyboardButton(text="Избранное", callback_data="saved"),
                     InlineKeyboardButton(text="Выйти из аккаунта", callback_data="logout"),
                     )
    menu_buttons.adjust(2)
    auth_button = InlineKeyboardButton(text="Войти", callback_data="auth")
