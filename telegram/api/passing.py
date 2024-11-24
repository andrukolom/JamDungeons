from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import html

from telegram.objects.callback_data import LocationCallback
from telegram.api.quest import ManyQuestsApi


class PassingApi(ManyQuestsApi):
    def __init__(self, query, method='get', data=None, page=1):
        super().__init__(query, method, data, page)
        self.type_api = 'passing'

    async def _generate_message_with_buttons(self):
        await self._init_api_data()
        self.buttons = InlineKeyboardBuilder()
        character_index = 1

        for quest in self._page_data:
            self.text += self._dash_separator
            self.text += await self._get_short_quest_description(quest) + '\n'
            self.text += "Твои персонажи:\n"
            for character in quest['characters']:
                self.text += html.bold(f"{character_index}. {html.quote(character['name'])}")
                self.text += " - остановился на локации: " + html.quote(character['location_now_name']) + '\n'
                self.buttons.add(InlineKeyboardButton(text=str(character_index), callback_data=LocationCallback(
                    id=character['location_now_id'], character_id=character['id']).pack()))
                character_index += 1
            self.text += '\n'
            self.buttons.adjust(5)
