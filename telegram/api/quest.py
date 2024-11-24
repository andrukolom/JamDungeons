from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import html

from telegram.objects.callback_data import CharacterCallback, QuestCallback, FavoriteCallback
from telegram.storage import TelegramStorage
from telegram.api.base import BaseManyObjectsApi
from telegram.api.request import RequestApi


class ManyQuestsApi(BaseManyObjectsApi):

    def __init__(self, query, method='get', data=None, page=1):
        super().__init__(query, method, data, page)
        self.type_api = 'many_quests'

    async def _generate_message_with_buttons(self):
        await self._init_api_data()
        self.text = ""
        self.buttons = InlineKeyboardBuilder()
        for index, quest in enumerate(self._page_data, 1):
            self.text += self._dash_separator
            self.text += html.bold(str(index) + '. ')
            self.text += await self._get_short_quest_description(quest) + '\n'
            self.buttons.add(InlineKeyboardButton(text=str(index), callback_data=QuestCallback(id=quest['id']).pack()))

    async def _get_short_quest_description(self, quest):
        text = await self._get_title_quest(quest)
        text += self._x_separator
        if len(quest['description']) > 64:
            text += html.quote(quest['description'][:64].strip()) + '...'
        else:
            text += html.quote(quest['description'])
        text += '\n'
        text += html.underline(html.quote(quest['author_name'])) + '\n'
        return text


class OneQuestApi(RequestApi):
    def __init__(self, query, telegram_id, method='get', data=None):
        super().__init__(query, method, data)
        self.type_api = 'one_quest'
        self._telegram_id = telegram_id
        self.tags = []

    async def _get_tags(self):
        tags = RequestApi(f"/tags?quest_id={self._page_data['id']}")
        self.tags = await tags.get_message()

    async def _get_full_quest_description(self, quest):
        text = await self._get_title_quest(quest)
        text += self._x_separator
        text += html.quote(quest['description']) + '\n\n'
        text += html.underline(html.italic(quest['author_name']))
        return text

    async def _button_favorite(self):
        print(f"/favorite/check?telegram_id={self._telegram_id}&quest_id={self._page_data['id']}")
        check = RequestApi(f"/favorite/check?telegram_id={self._telegram_id}&quest_id={self._page_data['id']}")
        check = await check.get_message()
        if not check:
            self.buttons.add(InlineKeyboardButton(text="Добавить в избранное",
                                                  callback_data=FavoriteCallback(quest_id=self._page_data['id'],
                                                                                 add=True).pack()))
        else:
            self.buttons.add(InlineKeyboardButton(text="Удалить из избранного",
                                                  callback_data=FavoriteCallback(quest_id=self._page_data['id'],
                                                                                 add=False).pack()))

    async def _init_api_data(self):
        response = await self._function[self._method]()
        if not response:
            self._valid = False
            return
        self._valid = True
        self._page_data = response[0]

    async def get_message(self):
        await self._init_api_data()
        await self._get_tags()
        self.text = await self._get_full_quest_description(self._page_data)
        if self.tags:
            self.text += f"\n#{' #'.join(self.tags)}"
        self.buttons = InlineKeyboardBuilder()
        self.buttons.add(
            InlineKeyboardButton(text="Пройти квест",
                                 callback_data=CharacterCallback(quest_id=self._page_data['id']).pack()))
        await self._button_favorite()
        self.buttons.row(TelegramStorage.to_menu_button)
