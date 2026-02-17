# ABOUTME: Asyncio scheduler for weekly blog scraping digest
# ABOUTME: Mirrors newsletter scheduler structure - separate configurable schedule

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class BlogScheduler:
    """Schedules weekly blog scraping and digest delivery."""

    def __init__(
        self,
        bot,
        user_id: int,
        schedule_day: int = 6,
        schedule_hour: int = 21,
        schedule_minute: int = 0,
        processor_factory=None
    ):
        self.bot = bot
        self.user_id = user_id
        self.schedule_day = schedule_day
        self.schedule_hour = schedule_hour
        self.schedule_minute = schedule_minute
        self.processor_factory = processor_factory
        self._task: Optional[asyncio.Task] = None

    def _calculate_next_run(self, now: datetime) -> datetime:
        current_weekday = now.weekday()
        days_ahead = self.schedule_day - current_weekday

        if days_ahead == 0 and (now.hour, now.minute) >= (self.schedule_hour, self.schedule_minute):
            days_ahead = 7
        elif days_ahead < 0:
            days_ahead += 7

        next_run = now + timedelta(days=days_ahead)
        next_run = next_run.replace(
            hour=self.schedule_hour,
            minute=self.schedule_minute,
            second=0,
            microsecond=0
        )
        return next_run

    def _create_processor(self):
        from src.blog.processor import BlogProcessor
        from src.config import BLOG_SOURCES_FILE
        return BlogProcessor(sources_file=BLOG_SOURCES_FILE)

    async def start(self):
        """Start the scheduler loop."""
        logger.info(f"Starting blog scheduler (day={self.schedule_day}, hour={self.schedule_hour}:{self.schedule_minute:02d})")

        while True:
            try:
                now = datetime.now()
                next_run = self._calculate_next_run(now)
                wait_seconds = (next_run - now).total_seconds()

                logger.info(f"Next blog digest: {next_run} ({wait_seconds/3600:.1f}h from now)")
                await asyncio.sleep(wait_seconds)
                await self._run_digest()

            except asyncio.CancelledError:
                logger.info("Blog scheduler cancelled")
                break
            except Exception as e:
                logger.error(f"Blog scheduler error: {e}", exc_info=True)
                await asyncio.sleep(3600)

    async def _run_digest(self):
        """Execute blog processing and send Telegram digest."""
        logger.info("Starting blog digest processing...")

        try:
            processor = self._create_processor()
            result = processor.process()

            if result["success"]:
                summary = result["summary"]
                blog_count = result["blog_count"]

                header = f"📰 Tech Blog Digest - {blog_count} blogów z ostatniego tygodnia\n\n"
                message = header + summary

                from src.formatter import split_long_message
                for chunk in split_long_message(message):
                    await self.bot.send_message(self.user_id, chunk)

                logger.info("Blog digest sent successfully")
            else:
                error_msg = f"❌ Blog digest failed: {result.get('error', 'Unknown error')}"
                await self.bot.send_message(self.user_id, error_msg)

        except Exception as e:
            logger.error(f"Blog digest error: {e}", exc_info=True)
            try:
                await self.bot.send_message(self.user_id, f"❌ Blog digest error: {e}")
            except Exception:
                pass

    def stop(self):
        if self._task:
            self._task.cancel()
