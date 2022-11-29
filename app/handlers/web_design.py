from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text, IDFilter
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.config import load_config
from app.handlers.common import cmd_welcome, get_user_info, add_buttons


class OrderWeb(StatesGroup):
    waiting_order = State()
    waiting_phone = State()
    waiting_kind = State()
    waiting_text = State()
    waiting_size = State()
    waiting_info = State()
    waiting_voice = State()


order_kind = {
    "Визитка": "визитки",
    "Листовка": "листовки",
    "Сертификат": "сертификата",
    "Афиша/Плакат": "афиши/плаката",
    "Другое": "полиграфической продукции"
}


order_data = {
    "text": "",
    "docs": [],
    "photo": [],
    "voice": []
}


config = load_config("config/cfg.ini")
bot = Bot(token=config.bot.token)


async def order_start(message: types.Message, state: FSMContext):
    order_data['text'] = ''
    order_data['docs'] = []
    order_data['photo'] = []
    order_data['voice'] = []
    await OrderWeb.waiting_phone.set()
    await state.update_data(order_name="Дизайн для Интернета")
    await message.answer('🤓 У нас к вам всего пару вопросов! 🔷 Напишите контактный номер телефона.')


def register_handlers_print_design(dp: Dispatcher):
    dp.register_message_handler(order_start, Text(equals="Дизайн для Интернета"), state="*")
