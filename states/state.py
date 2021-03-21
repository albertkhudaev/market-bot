from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup

class EditState(StatesGroup):
    name = State()
    price = State()
    description = State()
    photo = State()

class NewState(StatesGroup):
    newcat = State()
    newsubcat = State()

class NewAdminState(StatesGroup):
    newadmin = State()
    deladmin = State()