from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from telegram.objects.middlewares import AuthMiddleware
from telegram.storage import TelegramStorage

router = Router()
router.message.middleware(AuthMiddleware())

@router.message(Command('menu'))
async def command_menu_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выбери нужное действие", reply_markup=TelegramStorage.menu_buttons.as_markup())