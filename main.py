import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, KeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import config
from handlers import tasks, time_entries
from callbacks.time_entries import *
from keyboards.tasks import NumbersCallbackFactory


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


async def main():
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(time_entries.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
