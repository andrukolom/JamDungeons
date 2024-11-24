from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from telegram.api.request import RequestApi
from aiogram.utils.keyboard import InlineKeyboardBuilder
from telegram.storage import TelegramStorage
from telegram.objects.fsm import SingleStatesGroup
import sqlite3

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message):
    builder = InlineKeyboardBuilder()
    if message.chat.id not in TelegramStorage.users:
        builder.add(TelegramStorage.auth_button)
        return await message.answer("Для начала тебе надо войти", reply_markup=builder.as_markup())
    await message.answer(f"Добро пожаловать, {message.chat.full_name}! Выбери действие", reply_markup=TelegramStorage.menu_buttons.as_markup())


@router.callback_query(F.data == "auth")
async def command_auth_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SingleStatesGroup.auth_get_key)
    await callback.answer()
    await callback.message.answer("Пришли мне свой ключ для входа")


@router.message(SingleStatesGroup.auth_get_key)
async def command_auth_get_key(message: Message, state: FSMContext):
    key = message.text
    check = RequestApi("/telegram/check_key", method='post', data={"key": key, "telegram_id": message.chat.id})
    check = await check.is_valid()
    if not check:
        return await message.answer("Не верный ключ, отправьте его без всяких подписей и проверьте, что он не устарел")

    with sqlite3.connect(TelegramStorage.db_path) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO users(id, nickname) VALUES(?, ?)", (message.chat.id, message.chat.username))
    TelegramStorage.users.append(message.chat.id)
    await state.clear()
    await message.answer("Вы удачно вошли в аккаунт! Выберите следующее действие", reply_markup=TelegramStorage.menu_buttons.as_markup())
