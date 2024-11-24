from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import html
from telegram.api.quest import ManyQuestsApi


class ManyAchievementsApi(ManyQuestsApi):

    def __init__(self, query, method='get', data=None, page=1):
        super().__init__(query, method, data, page)
        self.type_api = 'many_achievements'

    async def _generate_message_with_buttons(self):
        await self._init_api_data()
        self.text = ""
        self.buttons = InlineKeyboardBuilder()

        for quest in self._page_data:
            self.text += self._dash_separator
            self.text += await self._get_title_quest(quest)
            for achievement in quest['achievements']:
                self.text += html.underline(html.quote(f"{achievement['name']}\n"))
                self.text += f"(Получено: {achievement['date']})\n\n"
                # self.text += html.quote(f"> {achievement['description']}\n\n")
