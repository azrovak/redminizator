from aiogram import Router, html

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, DialogCalendar, DialogCalendarCallback, \
    get_user_locale
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.formatting import as_list, Bold, Url, as_line
from redminelib import Redmine

from config import config, redmine
from keyboards.common import get_accept_keyboard
from keyboards.tasks import get_tasks_links_keyboard, get_tasks_keyboard

router = Router()


class SetEntry(StatesGroup):
    choosing_task = State()
    choosing_date = State()
    choosing_hour = State()
    choosing_comment = State()


@router.message(Command('lastentries'))
async def last_entries_handler(msg: Message):
    user = redmine.user.get('current')
    l = []
    for i in (user.time_entries[:7]):
        l.append(Bold('Задача', ': ', i.issue.id, ' '))
        l.append(as_line(Bold('Дата'), ': ', i.spent_on, ' ',
                         Bold('Часы'), ': ', i.hours, ' ',
                         Bold('Комментарий'), ': ', i.comments))
    content = as_list(Bold('Последнии отметки времени'), *l)
    await msg.answer(**content.as_kwargs())


@router.message(Command('addentries'))
async def add_entries_handler(msg: Message, state: FSMContext):
    await msg.answer(**Bold('Выбери задачу:').as_kwargs(), reply_markup=get_tasks_keyboard('choosing_task'))
    await state.set_state(SetEntry.choosing_task)


@router.message(SetEntry.choosing_task)
async def choosing_task(message: Message):
    await message.answer(f'choosing_task ')
    # await state.set_state(SetEntry.choosing_date)
    # await callback.answer()


@router.message(SetEntry.choosing_comment)
async def choosing_comment(message: Message, state: FSMContext):
    entry_data = await state.get_data()
    await state.update_data(choosen_comment=message.text)
    content = as_list(Bold('Данные для добавления:'),
                      f'Задача: {entry_data["choosen_task"]}',
                      f'Дата: {entry_data["choosen_date"]}',
                      f'Часы: {entry_data["choosen_hour"]}',
                      f'Комментарий: {message.text}',
                      )
    await message.answer(**content.as_kwargs(),reply_markup=get_accept_keyboard((("Сохранить", "save_time_entry"),)))

    # await state.set_state(SetEntry.choosing_date)
    # await callback.answer()