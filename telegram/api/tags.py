from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from telegram.objects.callback_data import TagCallback
from telegram.storage import TelegramStorage


class TagsApi:

    def __init__(self, tags_data):
        self.type_api = 'many_tags'
        self._tags_data = tags_data
        self.selected_tags = self._tags_data.get('selected_tags', [])
        self._all_tags = TelegramStorage.base_tags + self._tags_data.get('new_tags', [])

    async def add_delete_tag(self, tag_now):
        if tag_now not in self.selected_tags and len(self.selected_tags) <= 10:
            self.selected_tags.append(tag_now)
        else:
            self.selected_tags.remove(tag_now)


    async def get_message(self):
        self.text = "Выбери нужные теги и нажми готово"
        self.buttons = InlineKeyboardBuilder()

        for tag in self._all_tags:
            button_text = tag
            if tag in self.selected_tags:
                button_text = '✅' + button_text
            self.buttons.add(InlineKeyboardButton(text=button_text, callback_data=TagCallback(tag_now=tag).pack()))
        self.buttons.adjust(2)
        self.buttons.row(InlineKeyboardButton(text="Добавить другие теги", callback_data="other_tags"),
                         InlineKeyboardButton(text="Готово", callback_data="finish_tags"))
        self.buttons.row(TelegramStorage.to_menu_button)
