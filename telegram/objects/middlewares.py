from aiogram import BaseMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram.storage import TelegramStorage

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, message, data):
        if message.chat.id in TelegramStorage.users:
            return await handler(message, data)
        builder = InlineKeyboardBuilder([[TelegramStorage.auth_button]])
        return await message.answer("Вы не зарегистрированы", reply_markup=builder.as_markup())

