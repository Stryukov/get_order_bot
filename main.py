import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from app.config import load_config
from app.handlers.common import register_handlers_common

logger = logging.getLogger(__name__)


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
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
