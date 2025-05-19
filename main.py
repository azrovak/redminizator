import asyncio
import datetime
import logging
import sys

from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, KeyboardButton, BotCommand
from aiogram.filters import Command
from aiogram.utils.formatting import Bold, as_list
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import config
from handlers import tasks, time_entries
from callbacks import time_entries as callback_te
from keyboards.common import get_accept_keyboard
from keyboards.tasks import NumbersCallbackFactory
from utils.date import all_date_between_dates
from utils.redmine import get_time_entries, get_empty_times, get_time_entry_today

#
# @router.message(Command('info'))
# async def info(message: Message):
#     await message.answer(f'Информация о текущей задаче по расписанию')
#
# @router.message(Command("reply_builder"))
# async def reply_builder(message: Message):
#     builder = ReplyKeyboardBuilder()
#     for i in range(1, 17):
#         builder.add(KeyboardButton(text=str(i)))
#     builder.adjust(3)
#     await message.answer(
#         "Выберите число:",
#         reply_markup=builder.as_markup(resize_keyboard=True),
#     )

#
# @time_entries.router.callback_query(NumbersCallbackFactory.filter(F.action == "choosing_task"))
# # @router.callback_query(F.data == "time_data2")
# async def callbacks_change_task_fab(callback: types.CallbackQuery, callback_data: NumbersCallbackFactory):
#
#     await callback.message.answer(f'Выбранная задача: {callback_data.value} ')
#     await callback.answer()

bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher(storage=MemoryStorage())
CHECKER_WEEK_FLAG = False
CHECKER_DAY_FLAG = True


async def set_main_menu(bot: Bot):
    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Start bot'),
        BotCommand(command='/tasks',
                   description='My list tasks'),
        BotCommand(command='/add_entries',
                   description='Add time entry'),
        BotCommand(command='/check_empty_times',
                   description='Check empty time entries'),
        BotCommand(command='/day_watcher_start',
                   description='Run watcher empty time entries'),
        BotCommand(command='/day_watcher_stop',
                   description='Stop check empty time entries'),
        BotCommand(command='/week_watcher_start',
                   description='Run watcher empty time entries'),
        BotCommand(command='/week_watcher_stop',
                   description='Stop check empty time entries'),
        BotCommand(command='/last_entries',
                   description='Last time entries')
    ]
    await bot.set_my_commands(main_menu_commands)


async def checker(chat_id, sleep_time):
    while CHECKER_WEEK_FLAG:
        _times = get_empty_times()
        if _times:
            content = as_list(Bold("Не заполнено расписание:"), *_times)
            await bot.send_message(chat_id, **content.as_kwargs())
        await asyncio.sleep(sleep_time)


async def checker_day(chat_id):
    while CHECKER_DAY_FLAG:
        _now = datetime.datetime.now(datetime.timezone.utc)
        if _now.isoweekday() > 6:
            return
        _now = _now.time()
        time_entry = get_time_entry_today()
        if not time_entry:
            if _now.hour==13 and _now.minute==30:
                content = as_list(Bold("Сегодня не заполнено расписание. Заполним?"))
                await bot.send_message(chat_id, **content.as_kwargs(),
                                       reply_markup=get_accept_keyboard(
                                       (("По новой задаче", "fill_empty_day_by_new_task"),
                                        ("По предыдущей метке",
                                         "fill_empty_day_by_last_task")),
                                       lines=2))
                await asyncio.sleep(60)
        await asyncio.sleep(20)


@dp.message(Command('check_empty_times'))
async def check_empty_times(msg: Message):
    _times = get_empty_times()
    if _times:
        content = as_list(Bold("Не заполнено расписание:"), *_times)
        await bot.send_message(msg.chat.id, **content.as_kwargs(),
                               reply_markup=get_accept_keyboard(
                                   (("По новой задаче", "fill_empty_entry_by_new_task"),
                                    ("По предыдущей метке",
                                     "fill_empty_entry_by_last_task")),
                                   lines=2))
    else:
        content = as_list("Всё расписание заполнено!", *[])
        await bot.send_message(msg.chat.id, **content.as_kwargs())


@dp.message(Command('week_watcher_start'))
async def week_watcher_start_handler(msg: Message):
    global CHECKER_WEEK_FLAG
    CHECKER_WEEK_FLAG = True
    asyncio.run_coroutine_threadsafe(checker(msg.chat.id, 14400), asyncio.get_event_loop())


@dp.message(Command('week_watcher_stop'))
async def week_watcher_stop_handler(msg: Message):
    global CHECKER_WEEK_FLAG
    CHECKER_WEEK_FLAG = False


@dp.message(Command('day_watcher_start'))
async def week_day_start_handler(msg: Message):
    global CHECKER_DAY_FLAG
    _now = datetime.datetime.now(datetime.timezone.utc).time()
    await msg.answer(f'{_now}')
    CHECKER_DAY_FLAG = True
    asyncio.run_coroutine_threadsafe(checker_day(msg.chat.id), asyncio.get_event_loop())


@dp.message(Command('day_watcher_stop'))
async def week_day_stop_handler(msg: Message):
    global CHECKER_DAY_FLAG
    CHECKER_DAY_FLAG = False


async def main():
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    dp.include_routers(time_entries.router, tasks.router, callback_te.router)
    await bot.delete_webhook(drop_pending_updates=True)
    dp.startup.register(set_main_menu)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
