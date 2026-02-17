# ABOUTME: Asyncio scheduler for weekly newsletter digest
# ABOUTME: Calculates next run time, triggers processing, handles errors

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class NewsletterScheduler:
    """Schedules weekly newsletter digest processing."""

    def __init__(
        self,
        bot,
        user_id: int,
        schedule_day: int = 6,  # 0=Monday, 6=Sunday
        schedule_hour: int = 20,
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
        """
        Calculate next scheduled run time.

        Args:
            now: Current datetime

        Returns:
            Next datetime when scheduler should run
        """
        # Get current weekday (0=Monday, 6=Sunday)
        current_weekday = now.weekday()

        # Calculate days until target day
        days_ahead = self.schedule_day - current_weekday

        # If target day is today but time has passed, schedule for next week
        if days_ahead == 0 and (now.hour, now.minute) >= (self.schedule_hour, self.schedule_minute):
            days_ahead = 7
        # If target day already passed this week, schedule for next week
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

    async def start(self):
        """Start the scheduler loop."""
        logger.info(f"Starting newsletter scheduler (day={self.schedule_day}, hour={self.schedule_hour})")

        while True:
            try:
                now = datetime.now()
                next_run = self._calculate_next_run(now)
                wait_seconds = (next_run - now).total_seconds()

                logger.info(f"Next newsletter digest: {next_run} ({wait_seconds/3600:.1f}h from now)")

                # Wait until scheduled time
                await asyncio.sleep(wait_seconds)

                # Run processing
                await self._run_digest()

            except asyncio.CancelledError:
                logger.info("Newsletter scheduler cancelled")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}", exc_info=True)
                # Wait 1 hour before retrying on error
                await asyncio.sleep(3600)

    async def _run_digest(self):
        """Execute newsletter processing and send to Telegram."""
        logger.info("Starting newsletter digest processing...")

        try:
            # Create processor (factory pattern for testing)
            if self.processor_factory:
                processor = self.processor_factory()
            else:
                from src.newsletter.processor import NewsletterProcessor
                from src.config import IMAP_HOST, IMAP_PORT, IMAP_USER, IMAP_PASSWORD, NEWSLETTER_SENDERS_FILE

                processor = NewsletterProcessor(
                    imap_host=IMAP_HOST,
                    imap_port=IMAP_PORT,
                    imap_user=IMAP_USER,
                    imap_password=IMAP_PASSWORD,
                    senders_file=NEWSLETTER_SENDERS_FILE
                )

            # Run processing (blocking, but runs in executor implicitly)
            result = processor.process()

            # Send result to Telegram
            if result["success"]:
                summary = result["summary"]
                email_count = result["email_count"]

                header = f"📬 Newsletter Digest - {email_count} maili z ostatniego tygodnia\n\n"
                message = header + summary

                # Split if too long (Telegram limit 4096 chars)
                from src.formatter import split_long_message
                chunks = split_long_message(message)

                for chunk in chunks:
                    await self.bot.send_message(self.user_id, chunk)

                logger.info("Newsletter digest sent successfully")
            else:
                error_msg = f"❌ Newsletter digest failed: {result.get('error', 'Unknown error')}"
                await self.bot.send_message(self.user_id, error_msg)
                logger.error(f"Processing failed: {result.get('error')}")

        except Exception as e:
            logger.error(f"Digest execution error: {e}", exc_info=True)
            error_msg = f"❌ Newsletter digest error: {str(e)}"

            try:
                await self.bot.send_message(self.user_id, error_msg)
            except Exception as send_error:
                logger.error(f"Failed to send error message: {send_error}")

    def stop(self):
        """Stop the scheduler."""
        if self._task:
            self._task.cancel()
