from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram.storage import TelegramStorage
from telegram.api.request import RequestApi
from telegram.objects.callback_data import ListOfQuestsCallback


class BaseManyObjectsApi(RequestApi):

    def __init__(self, query, method='get', data=None, page=1):
        super().__init__(query, method, data)
        self._page_now = page
        self._count_pages = 0
        self._main_data = {"query": self._query}
        self.text = ""
        self.buttons = InlineKeyboardBuilder()
        self.type_api = 'base_many_objects'

    async def get_arrow_buttons(self):
        row = []
        print(self._page_data)
        if self._page_now > 1:
            args = await self.__next_page(-1)
            row.append(
                InlineKeyboardButton(text="<<",
                                     callback_data=ListOfQuestsCallback(**args).pack()))
        if self._page_now < self._count_pages:
            args = await self.__next_page(1)
            row.append(
                InlineKeyboardButton(text=">>",
                                     callback_data=ListOfQuestsCallback(**args).pack()))
        self.buttons.row(*row)

    async def __next_page(self, step):
        new_main_data = self._main_data.copy()
        new_main_data['page_now'] += step
        return new_main_data

    async def _generate_message_with_buttons(self):
        await self._init_api_data()

    async def get_message(self):
        await self._generate_message_with_buttons()
        self.buttons.adjust(5)
        await self.get_arrow_buttons()
        self.buttons.row(TelegramStorage.to_menu_button)

    async def _init_api_data(self):
        query = self._query
        self._query += f"&page={self._page_now}"
        response = await self._function[self._method]()
        self._query = query
        if not response:
            return
        self._valid = True
        self._page_data = response['result']
        self._count_pages = response['pages']
        self._main_data['page_now'] = self._page_now
        self._main_data['type_api'] = self.type_api

    async def is_valid(self):
        await self._init_api_data()
        return self._valid and self._page_data
