from aiogram.dispatcher.filters.state import State, StatesGroup


class SendAnswer(StatesGroup):
    provider_answer = State()
    user_answer = State()
