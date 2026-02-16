# ABOUTME: Main entry point for Claude-RPI Telegram bridge bot
# ABOUTME: Initializes aiogram bot and dispatcher, registers handlers, starts polling

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram import F

from src.config import TELEGRAM_BOT_TOKEN
from src.bot import handle_message, handle_new_command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Initialize and start the bot."""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    # Register command handlers
    dp.message.register(handle_new_command, Command("new"))

    # Register message handler for all text messages
    dp.message.register(handle_message, F.text)

    logger.info("Starting Claude-RPI Bridge bot...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
