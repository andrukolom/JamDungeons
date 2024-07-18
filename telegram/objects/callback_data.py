from aiogram.filters.callback_data import CallbackData

class LocationCallback(CallbackData, prefix="location"):
    id: int
    character_id: int

class CharacterCallback(CallbackData, prefix="character"):
    quest_id: int

class CreateCharacterCallback(CallbackData, prefix="create_character"):
    quest_id: int