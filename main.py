# ABOUTME: Main entry point for Claude-RPI Telegram bridge bot
# ABOUTME: Initializes aiogram bot, registers handlers, starts scheduler, begins polling

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram import F

from src.config import (
    TELEGRAM_BOT_TOKEN,
    ALLOWED_USER_ID,
    NEWSLETTER_ENABLED,
    NEWSLETTER_SCHEDULE_DAY,
    NEWSLETTER_SCHEDULE_HOUR
)
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

    # Start newsletter scheduler if configured
    scheduler_task = None
    if NEWSLETTER_ENABLED:
        from src.newsletter.scheduler import NewsletterScheduler

        from src.config import NEWSLETTER_SCHEDULE_MINUTE
        scheduler = NewsletterScheduler(
            bot=bot,
            user_id=ALLOWED_USER_ID,
            schedule_day=NEWSLETTER_SCHEDULE_DAY,
            schedule_hour=NEWSLETTER_SCHEDULE_HOUR,
            schedule_minute=NEWSLETTER_SCHEDULE_MINUTE
        )

        scheduler_task = asyncio.create_task(scheduler.start())
        logger.info("Newsletter scheduler enabled")
    else:
        logger.info("Newsletter scheduler disabled (IMAP not configured)")

    try:
        await dp.start_polling(bot)
    finally:
        if scheduler_task:
            scheduler_task.cancel()
            try:
                await scheduler_task
            except asyncio.CancelledError:
                pass

        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
