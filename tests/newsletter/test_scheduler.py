# ABOUTME: Unit tests for asyncio-based newsletter scheduler
# ABOUTME: Tests next run calculation and error handling

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from src.newsletter.scheduler import NewsletterScheduler


class TestNewsletterScheduler:
    def test_calculate_next_run_same_week(self):
        """Test calculating next run when target day hasn't passed yet."""
        scheduler = NewsletterScheduler(
            bot=Mock(),
            user_id=123,
            schedule_day=6,  # Sunday
            schedule_hour=20
        )

        # Current: Wednesday 10:00
        now = datetime(2026, 2, 11, 10, 0, 0)  # Wednesday
        next_run = scheduler._calculate_next_run(now)

        # Should be: Sunday 20:00 same week
        expected = datetime(2026, 2, 15, 20, 0, 0)  # Sunday
        assert next_run == expected

    def test_calculate_next_run_next_week(self):
        """Test calculating next run when target day already passed."""
        scheduler = NewsletterScheduler(
            bot=Mock(),
            user_id=123,
            schedule_day=6,  # Sunday
            schedule_hour=20
        )

        # Current: Monday 10:00 (after Sunday)
        now = datetime(2026, 2, 16, 10, 0, 0)  # Monday
        next_run = scheduler._calculate_next_run(now)

        # Should be: Sunday next week
        expected = datetime(2026, 2, 22, 20, 0, 0)  # Next Sunday
        assert next_run == expected

    def test_calculate_next_run_with_minutes(self):
        """Test that schedule_minute is respected."""
        scheduler = NewsletterScheduler(
            bot=Mock(),
            user_id=123,
            schedule_day=6,  # Sunday
            schedule_hour=12,
            schedule_minute=10
        )

        # Current: Wednesday 10:00
        now = datetime(2026, 2, 11, 10, 0, 0)
        next_run = scheduler._calculate_next_run(now)

        expected = datetime(2026, 2, 15, 12, 10, 0)
        assert next_run == expected

    def test_calculate_next_run_same_day_before_minute(self):
        """When it's the right day/hour but before the minute, run today."""
        scheduler = NewsletterScheduler(
            bot=Mock(),
            user_id=123,
            schedule_day=6,  # Sunday
            schedule_hour=12,
            schedule_minute=10
        )

        # Current: Sunday 12:05 - before 12:10
        now = datetime(2026, 2, 15, 12, 5, 0)
        next_run = scheduler._calculate_next_run(now)

        expected = datetime(2026, 2, 15, 12, 10, 0)
        assert next_run == expected

    def test_calculate_next_run_same_day_after_minute(self):
        """When time has passed today, schedule for next week."""
        scheduler = NewsletterScheduler(
            bot=Mock(),
            user_id=123,
            schedule_day=6,  # Sunday
            schedule_hour=12,
            schedule_minute=10
        )

        # Current: Sunday 12:15 - after 12:10
        now = datetime(2026, 2, 15, 12, 15, 0)
        next_run = scheduler._calculate_next_run(now)

        expected = datetime(2026, 2, 22, 12, 10, 0)
        assert next_run == expected
