from aiogram.fsm.state import State, StatesGroup

class SingleStatesGroup(StatesGroup):
    auth_get_key = State()
    get_quest_id = State()
    new_character_name = State()
