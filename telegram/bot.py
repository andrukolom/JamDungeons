import asyncio
import sqlite3

import aiohttp
from dotenv import load_dotenv
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from routers import callbacks, auth, commands
from telegram.storage import TelegramStorage


async def main():
    with sqlite3.connect(TelegramStorage.db_path) as conn:
        cur = conn.cursor()
        users = cur.execute("SELECT id FROM users").fetchall()
        users = [x[0] for x in users]
        TelegramStorage.users = users

    load_dotenv()
    credentials = {'username': os.environ.get("API_USERNAME"), 'password': os.environ.get("API_PASSWORD")}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://127.0.0.1:8000/api/auth', data=credentials) as response:
            token = await response.json()

    TelegramStorage.api_auth = {"Authorization": f"Token {token['token']}"}

    os.environ.pop('API_USERNAME', None)
    os.environ.pop('API_PASSWORD', None)

    TOKEN = os.environ.get("BOT_TOKEN")
    bot = Bot(TOKEN)

    os.environ.pop('BOT_TOKEN', None)

    dp = Dispatcher()
    dp.include_routers(callbacks.router, auth.router, commands.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
