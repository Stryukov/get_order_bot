from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text, IDFilter
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dataclasses import dataclass


@dataclass
class User:
    user_id: int
    uname: str
    fullname: str
    is_bot: bool
    locale: str


class Order(StatesGroup):
    waiting_order = State()
    waiting_kind = State()
    waiting_text = State()
    waiting_size = State()
    waiting_info = State()


# config = load_config("config/cfg.ini")
# bot = Bot(token=config.tg_bot.token)


async def cmd_start(message: types.Message):
    await welcome_text(message)
    await cmd_welcome(message)


async def welcome_text(message: types.Message):
    await message.answer('Здравствуйте, на связи 🐳 "КИТ В ДЕЛЕ" и мы уже готовы принять ваш онлайн заказ!')


async def cmd_welcome(message: types.Message):
    await Order.waiting_order.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ["Дизайн для полиграфии", "Дизайн для Интернета", "Разработка текстов"]
    add_buttons(buttons, keyboard)
    await message.answer('🤓 Пожалуйста, выберите в разработке чего вам нужна помощь?', reply_markup=keyboard)


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено")
    await cmd_welcome(message)


def get_user_info(message: types.Message):
    return User(
        user_id=message.from_user.id,
        uname=message.from_user.username,
        fullname=message.from_user.full_name,
        is_bot=message.from_user.is_bot,
        locale=message.from_user.locale
    )


def add_buttons(buttons: list, keyboard: types.ReplyKeyboardMarkup):
    for button in buttons:
        keyboard.add(button)
    return keyboard


def register_handlers_common(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")
