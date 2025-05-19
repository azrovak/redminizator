from datetime import datetime

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import Bold, as_line, as_list
from aiogram_calendar import DialogCalendarCallback, DialogCalendar, get_user_locale, SimpleCalendar, \
    SimpleCalendarCallback
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import StateFilter

from config import redmine
from states.entry import SetEntry, SetDayEntry
from keyboards.common import get_buttons_keyboard, get_accept_keyboard
from keyboards.tasks import NumbersCallbackFactory, get_tasks_keyboard
from utils.redmine import get_time_entries, get_empty_times

router = Router()


async def get_last_entries(count: int):
    last_entr = get_time_entries()
    l = []
    for i in last_entr[:count]:
        l.append(Bold(f'Задача: {redmine.issue.get(i.issue.id).subject} ({i.issue.id}) '))
        l.append(as_line(Bold('Дата'), f': {i.spent_on} ',
                         Bold('Часы'), f': {i.hours} ',
                         Bold('Комментарий'), f': {i.comments}')
                 )
    content = as_list(Bold('Последнии отметки времени'), *l)
    return content


@router.callback_query(NumbersCallbackFactory.filter(F.action == "choosing_task"), SetEntry.choosing_task)
async def callbacks_choosing_task(
        callback_query: types.CallbackQuery,
        callback_data: NumbersCallbackFactory,
        state: FSMContext
):
    await callback_query.message.answer(f'Выбранная задача: {callback_data.value}\nВыбери дату: ',
                                        reply_markup=await SimpleCalendar(
                                            locale=await get_user_locale(callback_query.from_user)
                                        ).start_calendar())
    await state.set_state(SetEntry.choosing_date)
    await state.update_data(choosen_task=callback_data.value)
    await callback_query.answer()


#
@router.callback_query(SetEntry.choosing_date, DialogCalendarCallback.filter())
async def callbacks_choosing_date(
        callback_query: types.CallbackQuery,
        callback_data: CallbackData,
        state: FSMContext
):
    selected, date = await DialogCalendar(locale=await get_user_locale(callback_query.from_user)).process_selection(
        callback_query, callback_data)
    if selected:
        await state.set_state(SetEntry.choosing_hour)
        await state.update_data(choosen_date=date)
        await callback_query.message.answer(f'Выбранная дата: {date.strftime("%d/%m/%Y")} \nВыбери время:',
                                            reply_markup=get_buttons_keyboard((2, 4, 6, 8), 'choosing_hour'))


@router.callback_query(SimpleCalendarCallback.filter())
async def callbacks_choosing_date_sc(
        callback_query: types.CallbackQuery,
        callback_data: CallbackData,
        state: FSMContext
):
    selected, date = await SimpleCalendar(locale=await get_user_locale(callback_query.from_user)).process_selection(
        callback_query, callback_data)
    if selected:
        await state.set_state(SetEntry.choosing_hour)
        await state.update_data(choosen_date=date.date())
        await callback_query.message.answer(f'Выбранная дата: {date.strftime("%d/%m/%Y")} \nВыбери время:',
                                            reply_markup=get_buttons_keyboard((2, 4, 6, 8), 'choosing_hour'))


@router.callback_query(NumbersCallbackFactory.filter(F.action == "choosing_hour"), SetEntry.choosing_hour)
async def callbacks_choosing_hour(
        callback_query: types.CallbackQuery,
        callback_data: NumbersCallbackFactory,
        state: FSMContext
):
    entry_data = await state.get_data()
    entry = redmine.time_entry.filter(issue_id=int(entry_data["choosen_task"]))[:1][0]
    await callback_query.message.answer(
        f'Выбранное время: {callback_data.value} \nПредыдущий комментарий: {entry.comments}'
        f'\nЗаполни комментарий:',
        reply_markup=get_accept_keyboard((("Без комментария", "save_time_entry"),
                                          ("Оставить предыдущий", "save_time_entry_last")), lines=2))
    await state.set_state(SetEntry.choosing_comment)
    # await state.set_state(SetDayEntry.choosing_comment)
    await state.update_data(choosen_hour=callback_data.value)
    await callback_query.answer()


@router.callback_query(
    StateFilter(SetEntry.choosing_comment, SetDayEntry.choosing_comment),
    F.data == "save_time_entry")
async def save_entry(
        callback_query: types.CallbackQuery,
        state: FSMContext
):
    entry_data = await state.get_data()
    redmine.time_entry.create(issue_id=entry_data["choosen_task"],
                              hours=entry_data["choosen_hour"],
                              spent_on=entry_data["choosen_date"],
                              comments=entry_data.get("choosen_comment", ''))
    await state.clear()
    content = await get_last_entries(1)
    await callback_query.message.answer(**content.as_kwargs())
    await callback_query.answer()


@router.callback_query(StateFilter(SetEntry.choosing_comment, SetDayEntry.choosing_comment),F.data == "save_time_entry_last")
async def save_time_entry_last(
        callback_query: types.CallbackQuery,
        state: FSMContext
):
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


@router.callback_query(F.data == "fill_empty_entry_by_new_task")
async def fill_empty_entry_by_new_task(
        callback_query: types.CallbackQuery,
        state: FSMContext
):
    await callback_query.message.answer(**Bold('Выбери задачу:').as_kwargs(),
                                        reply_markup=get_tasks_keyboard('choosing_task'))
    await state.set_state(SetEntry.choosing_task)
    await callback_query.answer()


@router.callback_query(F.data == "fill_empty_entry_by_last_task")
async def fill_empty_entry_by_last_task(
        callback_query: types.CallbackQuery,
        state: FSMContext
):
    last_entry = get_time_entries()[:1][0]
    _times = get_empty_times()
    for _time in _times:
        redmine.time_entry.create(issue_id=last_entry.issue.id,
                                  hours=last_entry.hours,
                                  spent_on=datetime.fromisoformat(_time).date(),
                                  comments=last_entry.comments)
    await callback_query.answer()


@router.callback_query(NumbersCallbackFactory.filter(F.action == "day_choosing_task"), SetDayEntry.choosing_task)
async def callbacks_day_change_time(
        callback_query: types.CallbackQuery,
        callback_data: NumbersCallbackFactory,
        state: FSMContext
):
    await state.update_data(choosen_task=callback_data.value)
    await state.set_state(SetDayEntry.choosing_hour)
    await callback_query.message.answer(f'Выбранная задача: {callback_data.value}\nВыбери время:',
                                        reply_markup=get_buttons_keyboard((2, 4, 6, 8), 'choosing_hour'))



@router.callback_query(NumbersCallbackFactory.filter(F.action == "choosing_hour"), SetDayEntry.choosing_hour)
async def callbacks_day_choosing_hour(
        callback_query: types.CallbackQuery,
        callback_data: NumbersCallbackFactory,
        state: FSMContext
):
    entry_data = await state.get_data()
    entry = redmine.time_entry.filter(issue_id=int(entry_data["choosen_task"]))[:1][0]
    await callback_query.message.answer(
        f'Выбранное время: {callback_data.value} \nПредыдущий комментарий: {entry.comments}'
        f'\nЗаполни комментарий:',
        reply_markup=get_accept_keyboard((("Без комментария", "save_time_entry"),
                                          ("Оставить предыдущий", "save_time_entry_last")), lines=2))
    await state.set_state(SetDayEntry.choosing_comment)
    await state.update_data(choosen_hour=callback_data.value)
    await callback_query.answer()


@router.callback_query(F.data == "fill_empty_day_by_new_task")
async def fill_empty_entry_by_new_task(
        callback_query: types.CallbackQuery,
        state: FSMContext
):
    await callback_query.message.answer(**Bold('Выбери задачу:').as_kwargs(),
                                        reply_markup=get_tasks_keyboard('day_choosing_task'))
    await state.set_state(SetDayEntry.choosing_task)
    await state.update_data(choosen_date=datetime.now().date())
    await callback_query.answer()

@router.callback_query(F.data == "fill_empty_day_by_last_task")
async def fill_empty_entry_by_last_task(
        callback_query: types.CallbackQuery,
        state: FSMContext
):
    last_entry = get_time_entries()[:1][0]
    redmine.time_entry.create(issue_id=last_entry.issue.id,
                              hours=last_entry.hours,
                              spent_on=datetime.now().date(),
                              comments=last_entry.comments)
    await callback_query.message.answer("Заполнил!")
    await callback_query.answer()
