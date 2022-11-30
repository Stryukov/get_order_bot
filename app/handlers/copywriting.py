from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text, IDFilter
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.config import load_config
from app.handlers.common import cmd_welcome, get_user_info


class OrderCopy(StatesGroup):
    waiting_order = State()
    waiting_phone = State()
    waiting_kind = State()
    waiting_text = State()
    waiting_size = State()
    waiting_voice = State()


order_data = {
    "text": "",
    "voice": []
}


config = load_config("config/cfg.ini")
bot = Bot(token=config.bot.token)


async def order_start(message: types.Message, state: FSMContext):
    order_data['text'] = ''
    order_data['docs'] = []
    order_data['photo'] = []
    order_data['voice'] = []
    await OrderCopy.waiting_phone.set()
    await state.update_data(order_name="Разработка текстов")
    await message.answer('🤓 У нас к вам всего пару вопросов! 🔷 Напишите контактный номер телефона.')


async def get_phone(message: types.Message, state: FSMContext):
    await OrderCopy.next()
    await state.update_data(order_phone=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Пост в соц сетях', 'Рассылка', 'Доска объявлений', 'Сайт (seo статья)']
    keyboard.add(*buttons)
    await message.answer('🔷 Выберите, для чего вам нужны тексты?', reply_markup=keyboard)


async def get_kind(message: types.Message, state: FSMContext):
    await OrderCopy.next()
    await state.update_data(order_kind=message.text)
    await message.answer(f'🔷 Пришлите, пожалуйста, сюда все важные для вас тезисы к тексту. \n'
                         f'❗️<b>Важно!</b> На этом шаге можно прислать только текстовое сообщение. '
                         f'Аудио можно отправить далее.', parse_mode=types.ParseMode.HTML)


async def get_text(message: types.Message, state: FSMContext):
    await OrderCopy.next()
    await state.update_data(order_text=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Короткий (до 1000)", "«Как пост» (1000-1500)", "Длинный текст (2500)", "Свой вариант"]
    keyboard.add(*buttons)
    await message.answer('🔷 Теперь выберите размер для вашего текста (указано в символах).',
                         reply_markup=keyboard, parse_mode=types.ParseMode.HTML)


async def get_size(message: types.Message, state: FSMContext):
    await OrderCopy.next()
    await state.update_data(order_size=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add("Отправить заявку")
    await message.answer('🔷 Если вас есть <b>важные детали</b> и нюансы, то '
                         '<b>наговорите нам их сюда в виде аудио</b>, '
                         'нам будет приятно вас услышать.🌸 '
                         'Потом нажмите кнопку "Отправить заявку"'
                         , reply_markup=keyboard, parse_mode=types.ParseMode.HTML)


async def get_voice(message: types.Message, state: FSMContext):
    if message.content_type == 'voice':
        order_data['voice'].append(message.voice.file_id)
        await state.update_data(order_voice=order_data['voice'])
    else:
        await message.answer('🔷 Пришлите голосовое сообщение или нажмите кнопку "Отправить заявку".')


async def order_finish(message: types.Message, state: FSMContext):
    order = await state.get_data()
    user = get_user_info(message)
    await bot.send_message(config.bot.admin_group, f'🔷 <b>Новый заказ!</b> '
                                                   f'\nКлиент: {user.fullname} (@{user.uname}) \n'
                                                   f'Контактный номер: {order["order_phone"]}'
                                                   f'\n{order["order_name"]}: '
                                                   f'{order["order_kind"]} / {order["order_size"]}'
                                                   f'\nТезисы: {order["order_text"]}',
                           parse_mode=types.ParseMode.HTML)
    if "order_voice" in order.keys():
        if order["order_voice"]:
            for voice in order['order_voice']:
                await bot.send_voice(config.bot.admin_group, voice)
    await message.answer('Спасибо за ваш заказ! Мы отнесемся к нему креативно!')
    await state.finish()
    await cmd_welcome(message)


def register_handlers_copywriting(dp: Dispatcher):
    dp.register_message_handler(order_start, Text(equals="Разработка текстов"), state="*")
    dp.register_message_handler(get_phone, state=OrderCopy.waiting_phone)
    dp.register_message_handler(get_kind, state=OrderCopy.waiting_kind)
    dp.register_message_handler(get_text, state=OrderCopy.waiting_text)
    dp.register_message_handler(get_size, state=OrderCopy.waiting_size)
    dp.register_message_handler(order_finish, Text(equals="Отправить заявку"), state=OrderCopy.waiting_voice)
    dp.register_message_handler(get_voice, state=OrderCopy.waiting_voice, content_types=types.ContentTypes.ANY)
