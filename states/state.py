from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup

class EditState(StatesGroup):
    name = State()
    price = State()
    description = State()