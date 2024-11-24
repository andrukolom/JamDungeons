from aiogram.fsm.state import State, StatesGroup

class SingleStatesGroup(StatesGroup):
    auth_get_key = State()
    new_character_name = State()

class FindQuestStatesGroup(StatesGroup):
    get_quest_id = State()
    get_quest_name = State()
    get_all_quests = State()
    get_tags = State()