from aiogram import Bot, Dispatcher, types
from aiogram.types import InputMediaPhoto
from aiogram.dispatcher.filters import Text, IDFilter
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.config import load_config
from app.handlers.common import cmd_welcome, get_user_info


class OrderPrint(StatesGroup):
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
    await OrderPrint.waiting_phone.set()
    await state.update_data(order_name="Дизайн для полиграфии")
    await message.answer('🤓 У нас к вам всего пару вопросов! 🔷 Напишите контактный номер телефона.')


async def get_phone(message: types.Message, state: FSMContext):
    await OrderPrint.next()
    await state.update_data(order_phone=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = order_kind.keys()
    keyboard.add(*buttons)
    await message.answer('🔷 Выберите, для чего нужно изготовить дизайн макет?', reply_markup=keyboard)


async def get_kind(message: types.Message, state: FSMContext):
    await OrderPrint.next()
    await state.update_data(order_kind=message.text)
    order_kind_dative = order_kind[message.text]
    await message.answer(f'🔷 Пришлите, пожалуйста, сюда весь текст для вашей '
                         f'<b>{order_kind_dative} в одном сообщении</b>. '
                         f'Если у вашей {order_kind_dative} две стороны, то укажите это в тексте. \n '
                         f'❗️<b>Важно!</b> После изготовления макета дизайна, текст не подлежит правкам. '
                         f'Пожалуйста, проверьте его сразу.', parse_mode=types.ParseMode.HTML)


async def get_text(message: types.Message, state: FSMContext):
    await OrderPrint.next()
    await state.update_data(order_text=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["A6 (10*15 см)", "A5 (15*20 см)", "A4 (21*30 см)", "Евроформат (10*21 см)", "Свой размер"]
    keyboard.add(*buttons)
    await message.answer('🔷 Теперь выберите размер для вашего дизайн макета',
                         reply_markup=keyboard, parse_mode=types.ParseMode.HTML)


async def get_size(message: types.Message, state: FSMContext):
    await OrderPrint.next()
    await state.update_data(order_size=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add("Отправить материалы")
    await message.answer('🔷 <b>Ваша заявка почти готова!</b> \n '
                         'Осталось только прислать, необходимые для вашего '
                         'макета материалы (логотипы, фото, картинки). \n '
                         '❗️<b>Важно!</b> <i>Можете прислать в виде картинок, а также ссылок на материалы.</i>',
                         reply_markup=keyboard, parse_mode=types.ParseMode.HTML)


async def get_info(message: types.Message, state: FSMContext):
    if message.content_type == 'text':
        order = await state.get_data()
        order_data['text'] += f'{order["order_text"]}, ' + message.text
        await state.update_data(order_text=order_data['text'])
    if message.content_type == 'document':
        order_data['docs'].append(message.document.file_id)
        await state.update_data(order_docs=order_data['docs'])
    if message.content_type == 'photo':
        order_data['photo'].append(message.photo[0].file_id)
        await state.update_data(order_photo=order_data['photo'])
    if message.content_type == 'sticker':
        await message.answer('Я робот для приема заказов. Мне стикеры не к чему.')
    if message.content_type == 'voice':
        order_data['voice'].append(message.voice.file_id)
        await state.update_data(order_voice=order_data['voice'])


async def welcome_voice(message: types.Message, state: FSMContext):
    await OrderPrint.next()
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
                                                   f'\nТекст макета: {order["order_text"]}',
                           parse_mode=types.ParseMode.HTML)
    if "order_docs" in order.keys():
        if order["order_docs"]:
            for doc in order['order_docs']:
                await bot.send_document(config.bot.admin_group, doc)
    if "order_photo" in order.keys():
        if order["order_photo"]:
            if len(order['order_photo']) > 1:
                media = []
                for photo in order['order_photo']:
                    media.append(InputMediaPhoto(photo))
                await bot.send_media_group(config.bot.admin_group, media)
            else:
                await bot.send_photo(config.bot.admin_group, order['order_photo'][0])
    if "order_voice" in order.keys():
        if order["order_voice"]:
            for voice in order['order_voice']:
                await bot.send_voice(config.bot.admin_group, voice)
    await message.answer('Спасибо за ваш заказ! Мы отнесемся к нему креативно!')
    await state.finish()
    await cmd_welcome(message)


def register_handlers_print_design(dp: Dispatcher):
    dp.register_message_handler(order_start, Text(equals="Дизайн для полиграфии"), state="*")
    dp.register_message_handler(get_phone, state=OrderPrint.waiting_phone)
    dp.register_message_handler(get_kind, state=OrderPrint.waiting_kind)
    dp.register_message_handler(get_text, state=OrderPrint.waiting_text)
    dp.register_message_handler(get_size, state=OrderPrint.waiting_size)
    dp.register_message_handler(welcome_voice, Text(equals="Отправить материалы"), state=OrderPrint.waiting_info)
    dp.register_message_handler(get_info, state=OrderPrint.waiting_info, content_types=types.ContentTypes.ANY)
    dp.register_message_handler(order_finish, Text(equals="Отправить заявку"), state=OrderPrint.waiting_voice)
    dp.register_message_handler(get_voice, state=OrderPrint.waiting_voice, content_types=types.ContentTypes.ANY)
