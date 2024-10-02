from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from redminelib import Redmine

from config import config
from keyboards.tasks import NumbersCallbackFactory


def get_buttons_keyboard(list_value, action=None, factory=NumbersCallbackFactory):
    builder = InlineKeyboardBuilder()
    for i in list_value:
        builder.button(text=str(i), callback_data=factory(action=action, value=i))
    builder.adjust(1)
    return builder.as_markup()


def get_accept_keyboard(list_value, lines=1):
    builder = InlineKeyboardBuilder()
    for m, v in list_value:
        builder.button(text=m, callback_data=v)
    builder.adjust(lines)
    return builder.as_markup()
