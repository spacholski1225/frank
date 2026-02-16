# ABOUTME: Integration tests for newsletter processing pipeline
# ABOUTME: Tests full flow from email fetch to summary generation

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.newsletter.processor import NewsletterProcessor
from src.newsletter.email_fetcher import EmailData


class TestNewsletterProcessor:
    @patch('src.newsletter.processor.ClaudeRunner')
    @patch('src.newsletter.processor.EmailFetcher')
    def test_process_newsletters_full_flow(self, mock_fetcher_class, mock_runner_class):
        """Test complete newsletter processing pipeline."""
        # Mock email fetching
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher

        mock_emails = [
            EmailData(
                sender="news@example.com",
                subject="Weekly Update",
                date=datetime(2026, 2, 10),
                body_text="Plain text",
                body_html="<p>HTML content</p>",
                message_id="<id1@example.com>"
            )
        ]
        mock_fetcher.fetch_last_week.return_value = mock_emails

        # Mock Claude analysis
        mock_runner = MagicMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.analyze_newsletters.return_value = "Analysis output"

        processor = NewsletterProcessor(
            imap_host="imap.test.com",
            imap_port=993,
            imap_user="user",
            imap_password="pass"
        )

        result = processor.process()

        assert result["success"] is True
        assert result["email_count"] == 1
        assert "folder" in result
        assert "summary" in result

        # Verify workflow
        mock_fetcher.fetch_last_week.assert_called_once()
        mock_runner.analyze_newsletters.assert_called_once()
