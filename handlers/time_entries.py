from aiogram import Router

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.formatting import as_list, Bold

from callbacks.time_entries import get_last_entries
from keyboards.common import get_accept_keyboard
from keyboards.tasks import get_tasks_keyboard
from states.entry import SetEntry, SetDayEntry

router = Router()


@router.message(Command('last_entries'))
async def last_entries_handler(msg: Message):
    content = await get_last_entries(5)
    await msg.answer(**content.as_kwargs())


@router.message(Command('add_entries'))
async def add_entries_handler(msg: Message, state: FSMContext):
    await msg.answer(**Bold('Выбери задачу:').as_kwargs(), reply_markup=get_tasks_keyboard('choosing_task'))
    await state.set_state(SetEntry.choosing_task)


@router.message(SetEntry.choosing_task)
async def choosing_task(message: Message):
    pass
    # await message.answer(f'choosing_task ')
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
    await message.answer(**content.as_kwargs(), reply_markup=get_accept_keyboard((("Сохранить", "save_time_entry"),)))

@router.message(SetDayEntry.choosing_comment)
async def choosing_comment(message: Message, state: FSMContext):
    entry_data = await state.get_data()
    await state.update_data(choosen_comment=message.text)
    content = as_list(Bold('Данные для добавления:'),
                      f'Задача: {entry_data["choosen_task"]}',
                      f'Часы: {entry_data["choosen_hour"]}',
                      f'Комментарий: {message.text}',
                      )
    await message.answer(**content.as_kwargs(),
                         reply_markup=get_accept_keyboard((("Сохранить", "save_time_entry"),)))

    # await state.set_state(SetEntry.choosing_date)
    # await callback.answer()
