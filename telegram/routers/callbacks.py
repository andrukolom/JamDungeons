import sqlite3

import aiohttp
from aiogram import F
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import html

from telegram.objects.callback_data import LocationCallback, CharacterCallback, CreateCharacterCallback
from telegram.objects.fsm import SingleStatesGroup
from telegram.objects.middlewares import AuthMiddleware
from telegram.storage import TelegramStorage

router = Router()
router.message.middleware(AuthMiddleware())


@router.callback_query(CharacterCallback.filter(F.quest_id))
async def callback_character(callback: CallbackQuery, callback_data: CharacterCallback):
    await callback.message.delete()
    await callback.answer("Вспоминаю ваших персонажей")
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"{TelegramStorage.base_url}/character?telegram_id={callback.message.chat.id}&quest_id={callback_data.quest_id}",
                headers=TelegramStorage.api_auth) as res:
            characters = await res.json()
    builder = InlineKeyboardBuilder()

    for character in characters:
        builder.add(InlineKeyboardButton(text=character['name'],
                                         callback_data=LocationCallback(id=character['location_now_id'],
                                                                        character_id=character['id']).pack()))
    builder.add(InlineKeyboardButton(text="Создать нового персонажа",
                                     callback_data=CreateCharacterCallback(quest_id=callback_data.quest_id).pack()))

    await callback.message.answer("Выберите персонажа для прохождения", reply_markup=builder.as_markup())


@router.callback_query(CreateCharacterCallback.filter(F.quest_id))
async def callback_create_character(callback: CallbackQuery, callback_data: CreateCharacterCallback, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.set_state(SingleStatesGroup.new_character_name)
    await state.update_data(quest_id=callback_data.quest_id)
    await callback.message.answer("Пришли имя для персонажа")


@router.message(SingleStatesGroup.new_character_name)
async def get_name_callback_create_character(message: Message, state: FSMContext):
    data = await state.get_data()
    async with aiohttp.ClientSession() as session:
        async with session.post(
                f"{TelegramStorage.base_url}/character/create",
                data={"quest_id": data['quest_id'], "character_name": message.text, "telegram_id": message.chat.id},
                headers=TelegramStorage.api_auth) as res:
            character = await res.json()
            character = character[0]

    builder = InlineKeyboardBuilder([[InlineKeyboardButton(text=f"Начать играть за {character['name']}",
                                         callback_data=LocationCallback(id=character['location_now_id'],
                                                                        character_id=character['id']).pack())]])
    await state.clear()
    await message.answer(f"Удачно создан {character['name']}", reply_markup=builder.as_markup())


@router.callback_query(LocationCallback.filter(F.id))
async def callback_location(callback: CallbackQuery, callback_data: LocationCallback):
    await callback.message.delete()
    location = callback_data.id
    await callback.answer()
    async with aiohttp.ClientSession() as session:
        async with session.post(
                f"{TelegramStorage.base_url}/get_location_and_save?id={location}&character_id={callback_data.character_id}",
                headers=TelegramStorage.api_auth) as res:
            location = await res.json()
            location = location[0]

        async with session.get(f"{TelegramStorage.base_url}/connect?from_location={location['id']}",
                               headers=TelegramStorage.api_auth) as res:
            next_locations = await res.json()
            next_locations = next_locations

    builder = InlineKeyboardBuilder()
    builder.adjust(2)
    for next_location in next_locations:
        builder.add(InlineKeyboardButton(text=next_location['action'],
                                         callback_data=LocationCallback(id=next_location['to_location'],
                                                                        character_id=callback_data.character_id).pack()))
    await callback.message.answer(location['text'], reply_markup=builder.as_markup())
    if location['the_end']:
        await callback.message.answer(
            "Финал! Как вам квест? <del>Возможно добавим кнопку отзыва</del> Выбери следующее действие",
            reply_markup=TelegramStorage.menu_buttons.as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "find_quest_by_id")
async def callback_find_quest_by_id(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(SingleStatesGroup.get_quest_id)
    await callback.answer()
    await callback.message.answer("Пришли мне id квеста")


@router.message(SingleStatesGroup.get_quest_id)
async def get_id_callback_find_quest_by_id(message: Message, state: FSMContext):  # TODO: Сделать проверку состояний
    if not message.text.isdigit():
        return await message.answer("Мне надо id")
    await state.clear()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{TelegramStorage.base_url}/quest?id={message.text}",
                               headers=TelegramStorage.api_auth) as res:
            quest = await res.json()
            if not quest:
                return await message.answer("Квеста с таким id нет", reply_markup=TelegramStorage.menu_buttons.as_markup())
            quest = quest[0]
    text = html.quote(quest['description'] + '\n\n' + quest['author_name'])
    text = html.bold(html.quote(quest['name'])) + '\n' + text
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Пройти квест", callback_data=CharacterCallback(quest_id=quest['id']).pack()))
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "logout")
async def callback_logout(callback: CallbackQuery):
    await callback.message.delete()
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{TelegramStorage.base_url}/logout_user", headers=TelegramStorage.api_auth,
                                data={"telegram_id": callback.message.chat.id}) as res:
            check = await res.json()
            if not check:
                return await callback.message.answer("Не удалось, попробуйте позже снова", reply_markup=TelegramStorage.menu_buttons.as_markup())

    with sqlite3.connect(TelegramStorage.db_path) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id=?", (callback.message.chat.id,))
    index = TelegramStorage.users.index(callback.message.chat.id)
    TelegramStorage.users.pop(index)
    builder = InlineKeyboardBuilder([[TelegramStorage.auth_button]])
    await callback.message.answer("Успешно вышли из аккаунта", reply_markup=builder.as_markup())
