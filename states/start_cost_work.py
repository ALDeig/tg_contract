from aiogram.dispatcher.filters.state import State, StatesGroup


class CostWork(StatesGroup):
    type_system = State()
    type_video = State()