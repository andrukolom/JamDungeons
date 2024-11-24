from aiogram.filters.callback_data import CallbackData


class LocationCallback(CallbackData, prefix="location"):
    id: int
    character_id: int


class QuestCallback(CallbackData, prefix="quest"):
    id: int


class ListOfQuestsCallback(CallbackData, prefix="list_of_quests"):
    page_now: int
    type_api: str


class CharacterCallback(CallbackData, prefix="character"):
    quest_id: int


class CreateCharacterCallback(CallbackData, prefix="create_character"):
    quest_id: int


class TagCallback(CallbackData, prefix="choose_tag"):
    tag_now: str


class FavoriteCallback(CallbackData, prefix="add_favorite"):
    quest_id: int
    add: bool
