from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from redminelib import Redmine

from config import config
from keyboards.tasks import get_tasks_links_keyboard

router = Router()


@router.message(Command('tasks'))
async def tasks_list_buttons(msg: Message):
    await msg.answer(f'Мои задачи', reply_markup=get_tasks_links_keyboard())
