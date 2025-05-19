from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import config
from utils.redmine import get_issues


class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
    action: str|None
    value: Optional[int] = None


def get_tasks_links_keyboard():
    builder = InlineKeyboardBuilder()
    for i in get_issues():
        builder.row(InlineKeyboardButton(
            text=i.subject, url=f"{config.host}/issues/{i.id}")
        )
    return builder.as_markup()


def get_tasks_keyboard(action=None):
    builder = InlineKeyboardBuilder()
    for i in get_issues():
        builder.button(text=i.subject, callback_data=NumbersCallbackFactory(action=action, value=i.id))
        # builder.button(text=i.subject, callback_data="time_data")
    builder.adjust(1)
    return builder.as_markup()
