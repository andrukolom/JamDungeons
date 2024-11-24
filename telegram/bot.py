import asyncio
import sqlite3

import aiohttp
from dotenv import load_dotenv
import os

from aiogram import Bot, Dispatcher

from routers import callbacks, auth, commands
from telegram.api.request import RequestApi
from telegram.storage import TelegramStorage


async def main():
    with sqlite3.connect(TelegramStorage.db_path) as conn:
        cur = conn.cursor()
        users = cur.execute("SELECT id FROM users").fetchall()
        users = [x[0] for x in users]
        TelegramStorage.users = users

    load_dotenv()
    credentials = {'username': os.environ.get("API_USERNAME"), 'password': os.environ.get("API_PASSWORD")}
    token = RequestApi("/auth", method='post', data=credentials)
    token = await token.get_message()

    TelegramStorage.api_auth = {"Authorization": f"Token {token['token']}"}

    os.environ.pop('API_USERNAME', None)
    os.environ.pop('API_PASSWORD', None)

    TOKEN = os.environ.get("BOT_TOKEN")
    bot = Bot(TOKEN)

    os.environ.pop('BOT_TOKEN', None)

    tags = RequestApi("/tag/base")
    tags = await tags.get_message()
    TelegramStorage.base_tags = tags

    dp = Dispatcher()
    dp.include_routers(callbacks.router, auth.router, commands.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
