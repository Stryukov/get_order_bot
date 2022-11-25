from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile, Message
from aiogram.dispatcher.filters import Text, IDFilter
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.deep_linking import get_start_link, decode_payload
from app.config import load_config
# from app.handlers.SQLighter import SQLighter
from dataclasses import dataclass
import os
import json
# import requests


@dataclass
class User:
    user_id: int
    uname: str
    fullname: str
    is_bot: bool
    locale: str


class Order(StatesGroup):
    waiting_order = State()


# config = load_config("config/cfg.ini")
# bot = Bot(token=config.tg_bot.token)


async def cmd_start(message: types.Message):
    await message.answer('hi')


def get_user_info(message: types.Message):
    return User(
        user_id=message.from_user.id,
        uname=message.from_user.username,
        fullname=message.from_user.full_name,
        is_bot=message.from_user.is_bot,
        locale=message.from_user.locale
    )


def register_handlers_common(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(cmd_start, commands="start")