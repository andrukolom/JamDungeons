import sqlite3
import urllib.parse
import aiohttp
from aiogram import F
from aiogram import html
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram.objects.callback_data import LocationCallback, CharacterCallback, CreateCharacterCallback, TagCallback, \
    QuestCallback, ListOfQuestsCallback, FavoriteCallback
from telegram.objects.fsm import SingleStatesGroup, FindQuestStatesGroup
from telegram.objects.middlewares import AuthMiddleware
from telegram.storage import TelegramStorage
from telegram.api.passing import PassingApi
from telegram.api.quest import ManyQuestsApi, OneQuestApi
from telegram.api.achievement import ManyAchievementsApi
from telegram.api.request import RequestApi
from telegram.api.tags import TagsApi

router = Router()
router.message.middleware(AuthMiddleware())


@router.callback_query(F.data == "menu")
async def callback_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    await callback.message.answer("Выбери нужное действие", reply_markup=TelegramStorage.menu_buttons.as_markup())


@router.callback_query(F.data == "my_achievements")
async def callback_my_achievements(callback: CallbackQuery):
    await callback.message.delete()
    achievements = ManyAchievementsApi(f"/achievements?telegram_id={callback.message.chat.id}")
    await achievements.get_message()
    await callback.answer()
    await callback.message.answer(achievements.text, reply_markup=achievements.buttons.as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "my_passing")
async def callback_my_passing(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    query = f"/passing?telegram_id={callback.message.chat.id}"
    page = PassingApi(query)
    await callback.answer()
    check = await page.is_valid()
    if not check:
        return await callback.message.answer("Вы пока ничего не проходили",
                                             reply_markup=TelegramStorage.menu_buttons.as_markup())
    await page.get_message()
    await state.update_data(query=query)
    await callback.message.answer(page.text, reply_markup=page.buttons.as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "favorite")
async def callback_get_favorite(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    query = f"/favorite?telegram_id={callback.message.chat.id}"
    page = ManyQuestsApi(query)
    await callback.answer()
    check = await page.is_valid()
    if not check:
        return await callback.message.answer("Вы пока ничего не сохранили в избранное",
                                             reply_markup=TelegramStorage.menu_buttons.as_markup())

    await state.update_data(query=query)
    await page.get_message()
    await callback.message.answer(page.text, reply_markup=page.buttons.as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(FavoriteCallback.filter())
async def callback_quest(callback: CallbackQuery, callback_data: FavoriteCallback):
    check = RequestApi(f"/favorite/{'add' if callback_data.add else 'delete'}", method='post',
                       data={"telegram_id": callback.message.chat.id, "quest_id": callback_data.quest_id})
    await callback.answer()
    check = await check.is_valid()
    if not check:
        if callback_data.add:
            text = "Не могу добавить в избранное, возможно он уже там"
        else:
            text = "Не получилось удалить"
        return await callback.message.answer(text)

    await callback.message.answer("Удачно выполнено")


@router.callback_query(QuestCallback.filter())
async def callback_quest(callback: CallbackQuery, callback_data: QuestCallback, state: FSMContext):
    query = f"/quest?id={callback_data.id}"
    quest = OneQuestApi(query, telegram_id=callback.message.chat.id)
    await state.update_data(query=query)
    await quest.get_message()
    await callback.answer()
    await callback.message.answer(quest.text, reply_markup=quest.buttons.as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(CharacterCallback.filter(F.quest_id))
async def callback_character(callback: CallbackQuery, callback_data: CharacterCallback):
    await callback.message.delete()
    await callback.answer("Вспоминаю ваших персонажей")
    characters = RequestApi(f"/character?telegram_id={callback.message.chat.id}&quest_id={callback_data.quest_id}")
    characters = await characters.get_message()

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
    character = RequestApi("/character/create", method='post', data={"quest_id": data['quest_id'], "character_name": message.text, "telegram_id": message.chat.id})
    character = await character.get_message()
    character = character[0]

    builder = InlineKeyboardBuilder([[InlineKeyboardButton(text=f"Начать играть за {character['name']}",
                                                           callback_data=LocationCallback(
                                                               id=character['location_now_id'],
                                                               character_id=character['id']).pack())]])
    await state.clear()
    await message.answer(f"Удачно создан {character['name']}", reply_markup=builder.as_markup())


@router.callback_query(LocationCallback.filter(F.id))
async def callback_location(callback: CallbackQuery, callback_data: LocationCallback):
    await callback.message.delete()
    location = callback_data.id
    await callback.answer()
    print(location, callback_data.character_id)
    location = RequestApi(f"/get_location_and_save", method='post', data={'id': location, 'character_id': callback_data.character_id})
    location = await location.get_message()
    location = location[0]

    next_locations = RequestApi(f"/connect?from_location={location['id']}")
    next_locations = await next_locations.get_message()

    builder = InlineKeyboardBuilder()
    builder.adjust(2)

    text = html.bold(html.quote(location['name'])) + '\n'
    text += html.quote(location['text']) + '\n\n'

    if next_locations:
        text += "Твои действия:\n"
    index = 1
    for next_location in next_locations:
        text += f"{index}. {next_location['action']}\n"
        builder.add(InlineKeyboardButton(text=str(index),
                                         callback_data=LocationCallback(id=next_location['to_location'],
                                                                        character_id=callback_data.character_id).pack()))
        index += 1

    await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    if location['achievement']:
        text = "Получено новое достижение!\n"
        text += location['achievement']['name'] + '\n' + location['achievement']['description']
        await callback.message.answer(text)
    if location['the_end']:
        await callback.message.answer(
            "Финал! Как вам квест? Выбери следующее действие",
            reply_markup=TelegramStorage.menu_buttons.as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "find_quest")
async def callback_find_quest(callback: CallbackQuery):
    await callback.message.delete()
    builder = InlineKeyboardBuilder([[InlineKeyboardButton(text="По имени", callback_data="find_quest_by_name"),
                                      InlineKeyboardButton(text="По id", callback_data="find_quest_by_id"),
                                      InlineKeyboardButton(text="По тегам", callback_data="find_quest_by_tags"), ]])
    builder.row(TelegramStorage.to_menu_button)
    await callback.answer()
    await callback.message.answer("Как искать будем?", reply_markup=builder.as_markup())


@router.callback_query(F.data == "find_quest_by_name")
async def callback_find_quest_by_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(FindQuestStatesGroup.get_quest_name)
    await callback.answer()
    await callback.message.answer("Пришли мне имя квеста")


@router.message(FindQuestStatesGroup.get_quest_name)
async def get_id_callback_find_quest_by_id(message: Message, state: FSMContext):
    await state.clear()
    query = f"/quest/name?name={message.text}"
    quest = ManyQuestsApi(query)
    check = await quest.is_valid()
    print(check)
    if not check:
        return await message.answer("Квестов с таким именем нет",
                                    reply_markup=TelegramStorage.menu_buttons.as_markup())

    await state.update_data(query=query)
    await quest.get_message()
    await message.answer(quest.text, reply_markup=quest.buttons.as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "find_quest_by_tags")
async def callback_find_quest_by_tags(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    data = await state.get_data()
    tags = TagsApi(data)
    await tags.get_message()
    await callback.answer()
    await callback.message.answer(tags.text, reply_markup=tags.buttons.as_markup())


@router.callback_query(TagCallback.filter())
async def callback_find_quest_by_tags_add_delete_tag(callback: CallbackQuery, callback_data: TagCallback,
                                                     state: FSMContext):
    data = await state.get_data()
    tags = TagsApi(data)
    await tags.add_delete_tag(callback_data.tag_now)
    await tags.get_message()
    await state.update_data(selected_tags=tags.selected_tags)
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=tags.buttons.as_markup())


@router.callback_query(F.data == "other_tags")
async def callback_find_quest_by_other_tags(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(FindQuestStatesGroup.get_tags)
    await callback.message.answer("Пришли мне сообщение с тегами, но не больше 10. Например:\n#отсылка #магия_вне_хогвартса")

@router.message(FindQuestStatesGroup.get_tags)
async def get_tags_callback_find_quest_by_tags(message: Message, state: FSMContext):
    new_tags = set()
    tags = message.text.split('#')[1:]
    len_tags = len(tags)
    i = 0
    while len(new_tags) <= 10 and i < len_tags:
        tag = tags[i].split()[0]
        new_tags.add(tag)
        i += 1

    buttons = InlineKeyboardBuilder()
    await state.set_state(None)
    if not new_tags:
        buttons.add(InlineKeyboardButton(text="Добавить", callback_data="other_tags"))
        buttons.add(InlineKeyboardButton(text="Выбрать из базовых", callback_data="find_quest_by_tags"))
        return await message.answer(f"Ничего не добавлено. Хотите добавить или выбрать из стандартных?", reply_markup=buttons.as_markup())

    await state.update_data(new_tags=list(new_tags))
    buttons.add(InlineKeyboardButton(text="Да, продолжить", callback_data="find_quest_by_tags"))
    buttons.add(InlineKeyboardButton(text="Нет, другие", callback_data="other_tags"))
    await message.answer(f"Вы хотите добавить: {', '.join(new_tags)}", reply_markup=buttons.as_markup())




@router.callback_query(F.data == "finish_tags")
async def callback_find_quest_by_tags_add_delete_tag(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    data = await state.get_data()
    await state.clear()
    tags = data.get('selected_tags', [])
    count_tags = len(tags)
    if count_tags > 10:
        await callback.message.answer("Не перестарался? Не больше 10 тегов можно, я возьму лишь первую десятку",
                                             reply_markup=TelegramStorage.menu_buttons.as_markup())
        count_tags = 10
        tags = tags[:10]
    query = ''
    for i in range(count_tags):
        query += f"tag{i}={urllib.parse.quote(tags[i])}&"
    query += f"count={count_tags}"

    query = f"/quest/tag?{query}"
    page = ManyQuestsApi(query)
    await callback.answer()
    check = await page.is_valid()
    if not check:
        return await callback.message.answer("Нет таких квестов", reply_markup=TelegramStorage.menu_buttons)

    await state.update_data(query=query)
    await page.get_message()
    await callback.message.answer(page.text, reply_markup=page.buttons.as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(ListOfQuestsCallback.filter())
async def callback_send_all_quests(callback: CallbackQuery, callback_data: ListOfQuestsCallback, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    api_class = {"many_quests": ManyQuestsApi,
                 # "one_quest": OneQuestApi,
                 "passing": PassingApi}

    data = await state.get_data()
    object = api_class[callback_data.type_api](data.get('query'), page=callback_data.page_now)
    check = await object.is_valid()
    if not check:
        return await callback.message.answer("Ой, что-то не так, не могу найти",
                                             reply_markup=TelegramStorage.menu_buttons.as_markup())
    await object.get_message()
    await callback.message.answer(object.text, reply_markup=object.buttons.as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "find_quest_by_id")
async def callback_find_quest_by_id(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(FindQuestStatesGroup.get_quest_id)
    await callback.answer()
    await callback.message.answer("Пришли мне id квеста")


@router.message(FindQuestStatesGroup.get_quest_id)
async def get_id_callback_find_quest_by_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Мне надо id")
    await state.clear()
    query = f"/quest?id={message.text}"
    quest = OneQuestApi(query, telegram_id=message.chat.id)
    check = await quest.is_valid()
    if not check:
        return await message.answer("Квеста с таким id нет",
                                    reply_markup=TelegramStorage.menu_buttons.as_markup())

    await state.update_data(query=query)
    await quest.get_message()
    await message.answer(quest.text, reply_markup=quest.buttons.as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "logout")
async def callback_logout(callback: CallbackQuery):
    await callback.message.delete()
    check = RequestApi("/logout_user", method='post', data={"telegram_id": callback.message.chat.id})
    check = await check.is_valid()
    if not check:
        return await callback.message.answer("Не удалось, попробуйте позже снова",
                                                     reply_markup=TelegramStorage.menu_buttons.as_markup())

    with sqlite3.connect(TelegramStorage.db_path) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id=?", (callback.message.chat.id,))
    index = TelegramStorage.users.index(callback.message.chat.id)
    TelegramStorage.users.pop(index)
    builder = InlineKeyboardBuilder([[TelegramStorage.auth_button]])
    await callback.message.answer("Успешно вышли из аккаунта", reply_markup=builder.as_markup())
