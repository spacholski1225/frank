# ABOUTME: Tests for blog scheduler
# ABOUTME: Verifies schedule calculation and Telegram delivery

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from src.blog.scheduler import BlogScheduler


def test_calculate_next_run_same_day_before_time():
    scheduler = BlogScheduler(bot=MagicMock(), user_id=123, schedule_day=6, schedule_hour=21, schedule_minute=0)
    # Sunday at 19:00, target is 21:00 same day
    now = datetime(2026, 2, 15, 19, 0)  # Sunday
    next_run = scheduler._calculate_next_run(now)
    assert next_run.day == 15
    assert next_run.hour == 21


def test_calculate_next_run_same_day_after_time():
    scheduler = BlogScheduler(bot=MagicMock(), user_id=123, schedule_day=6, schedule_hour=21, schedule_minute=0)
    # Sunday at 22:00, target 21:00 already passed -> next Sunday
    now = datetime(2026, 2, 15, 22, 0)
    next_run = scheduler._calculate_next_run(now)
    assert next_run.day == 22


@pytest.mark.asyncio
async def test_run_digest_sends_telegram_on_success():
    bot = MagicMock()
    bot.send_message = AsyncMock()
    scheduler = BlogScheduler(bot=bot, user_id=42, schedule_day=6, schedule_hour=21, schedule_minute=0)

    mock_result = {
        "success": True,
        "blog_count": 3,
        "summary": "great stuff"
    }

    with patch.object(scheduler, "_create_processor") as mock_factory:
        mock_processor = MagicMock()
        mock_processor.process.return_value = mock_result
        mock_factory.return_value = mock_processor
        await scheduler._run_digest()

    bot.send_message.assert_called()
    call_args = bot.send_message.call_args_list[0][0]
    assert call_args[0] == 42
    assert "3" in call_args[1]
