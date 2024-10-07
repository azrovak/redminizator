from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram_calendar import DialogCalendarCallback, DialogCalendar, get_user_locale, SimpleCalendar, \
    SimpleCalendarCallback
from aiogram.filters.callback_data import CallbackData

from config import redmine
from handlers import time_entries
from handlers.time_entries import SetEntry
from redmine_utils import get_last_entries
from keyboards.common import get_buttons_keyboard, get_accept_keyboard
from keyboards.tasks import NumbersCallbackFactory


@time_entries.router.callback_query(NumbersCallbackFactory.filter(F.action == "choosing_task"), SetEntry.choosing_task)
# @router.callback_query(F.data == "time_data2")
async def callbacks_change_task(callback_query: types.CallbackQuery, callback_data: NumbersCallbackFactory,
                                state: FSMContext):
    await callback_query.message.answer(f'Выбранная задача: {callback_data.value}\nВыбери дату: ',
                                        reply_markup=await SimpleCalendar(
                                            locale=await get_user_locale(callback_query.from_user)
                                        ).start_calendar())
    await state.set_state(SetEntry.choosing_date)
    await state.update_data(choosen_task=callback_data.value)
    await callback_query.answer()


#
@time_entries.router.callback_query(SetEntry.choosing_date, DialogCalendarCallback.filter())
async def callbacl_choosing_date(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, date = await DialogCalendar(locale=await get_user_locale(callback_query.from_user)).process_selection(
        callback_query, callback_data)
    if selected:
        await state.set_state(SetEntry.choosing_hour)
        await state.update_data(choosen_date=date)
        await callback_query.message.answer(f'Выбранная дата: {date.strftime("%d/%m/%Y")} \nВыбери время:',
                                            reply_markup=get_buttons_keyboard((2, 4, 6, 8), 'choosing_hour'))


@time_entries.router.callback_query(SimpleCalendarCallback.filter())
async def callbacl_choosing_date(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, date = await SimpleCalendar(locale=await get_user_locale(callback_query.from_user)).process_selection(
        callback_query, callback_data)
    if selected:
        await state.set_state(SetEntry.choosing_hour)
        await state.update_data(choosen_date=date.date())
        await callback_query.message.answer(f'Выбранная дата: {date.strftime("%d/%m/%Y")} \nВыбери время:',
                                            reply_markup=get_buttons_keyboard((2, 4, 6, 8), 'choosing_hour'))


@time_entries.router.callback_query(NumbersCallbackFactory.filter(F.action == "choosing_hour"), SetEntry.choosing_hour)
# @router.callback_query(F.data == "time_data2")
async def callbacks_change_task(callback_query: types.CallbackQuery, callback_data: NumbersCallbackFactory,
                                state: FSMContext):
    entry_data = await state.get_data()
    entry = redmine.time_entry.filter(issue_id=int(entry_data["choosen_task"]))[:1][0]
    await callback_query.message.answer(f'Выбранное время: {callback_data.value} \nПредыдущий комментарий: {entry.comments}'
                                        f'\nЗаполни комментарий:',
                                        reply_markup=get_accept_keyboard((("Без комментария", "save_time_entry"),
                                                                          ("Оставить предыдущий", "save_time_entry_last"))))
    await state.set_state(SetEntry.choosing_comment)
    await state.update_data(choosen_hour=callback_data.value)
    await callback_query.answer()


@time_entries.router.callback_query(F.data == "save_time_entry", SetEntry.choosing_comment)
async def save_entry(callback_query: types.CallbackQuery, state: FSMContext):
    entry_data = await state.get_data()
    redmine.time_entry.create(issue_id=entry_data["choosen_task"],
                              hours=entry_data["choosen_hour"],
                              spent_on=entry_data["choosen_date"],
                              comments=entry_data.get("choosen_comment", ''))
    await state.clear()
    content = await get_last_entries(1)
    await callback_query.message.answer(**content.as_kwargs())
    await callback_query.answer()


@time_entries.router.callback_query(F.data == "save_time_entry_last", SetEntry.choosing_comment)
async def save_entry(callback_query: types.CallbackQuery, state: FSMContext):
    entry_data = await state.get_data()
    entry = redmine.time_entry.filter(issue_id=int(entry_data["choosen_task"]))[:1][0]
    redmine.time_entry.create(issue_id=entry_data["choosen_task"],
                              hours=entry_data["choosen_hour"],
                              spent_on=entry_data["choosen_date"],
                              comments=entry.comments)
    await state.clear()
    content = await get_last_entries(1)
    await callback_query.message.answer(**content.as_kwargs())
    await callback_query.answer()