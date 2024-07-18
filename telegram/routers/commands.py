from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from telegram.objects.middlewares import AuthMiddleware
from telegram.storage import TelegramStorage

router = Router()
router.message.middleware(AuthMiddleware())

@router.message(Command('menu'))
async def command_menu_handler(message: Message):
    await message.answer("Выбери нужное действие", reply_markup=TelegramStorage.menu_buttons.as_markup())