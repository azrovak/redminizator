from aiogram.fsm.state import StatesGroup, State


class SetEntry(StatesGroup):
    choosing_task = State()
    choosing_date = State()
    choosing_hour = State()
    choosing_comment = State()

class SetDayEntry(StatesGroup):
    choosing_task = State()
    choosing_hour = State()
    choosing_comment = State()