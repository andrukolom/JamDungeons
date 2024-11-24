import aiohttp
from telegram.storage import TelegramStorage
from aiogram import html

class RequestApi:
    def __init__(self, query, method='get', data=None):
        self._data = data
        self._page_data = []
        self._query = query
        self._valid = False
        self.type_api = 'request'
        self._method = method
        self._function = {'get': self._get_method, 'post': self._post_method}
        # self._x_separator = '×' * 20 + '\n'
        self._x_separator = ''
        self._dash_separator = '-' * 20 + '\n'

    async def _get_method(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{TelegramStorage.base_url}{self._query}",
                                   headers=TelegramStorage.api_auth) as res:
                response = await res.json()
                print(response)
        return response

    async def _post_method(self):
        request = {"url": f"{TelegramStorage.base_url}{self._query}", "headers": TelegramStorage.api_auth}
        if self._data:
            request['data'] = self._data
        print(request)
        async with aiohttp.ClientSession() as session:
            async with session.post(**request) as res:
                response = await res.json()
                print(response)
        return response

    async def get_message(self):
        await self._init_api_data()
        return self._page_data

    async def _get_title_quest(self, quest):
        return html.bold(f"{html.quote(quest['name'])} - {quest['rating']}\n")

    async def _init_api_data(self):
        response = await self._function[self._method]()
        if not response:
            self._valid = False
            return
        self._valid = True
        self._page_data = response

    async def is_valid(self):
        await self._init_api_data()
        print(self._page_data)
        return self._valid