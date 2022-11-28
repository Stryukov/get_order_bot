import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from app.config import load_config
from app.handlers.common import register_handlers_common
from app.handlers.print_design import register_handlers_print_design
from aiogram.dispatcher.filters.state import State, StatesGroup

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="🚀 (пере)запустить бота"),
        BotCommand(command="/cancel", description="🛑 отменить текущее действие")
    ]
    await bot.set_my_commands(commands)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")
    config = load_config("config/cfg.ini")
    bot = Bot(token=config.bot.token)
    dp = Dispatcher(bot, storage=MemoryStorage())
    register_handlers_common(dp, config)
    register_handlers_print_design(dp)
    await set_commands(bot)
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
