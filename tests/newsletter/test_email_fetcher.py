# ABOUTME: Unit tests for IMAP email fetching functionality
# ABOUTME: Tests connection, date filtering, and email data extraction

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from src.newsletter.email_fetcher import EmailFetcher, EmailData


class TestEmailFetcher:
    @patch('src.newsletter.email_fetcher.imaplib.IMAP4_SSL')
    def test_fetch_emails_from_last_week(self, mock_imap_class):
        """Test fetching emails from the last 7 days."""
        # Setup mock IMAP connection
        mock_imap = MagicMock()
        mock_imap_class.return_value = mock_imap
        mock_imap.login.return_value = ('OK', [b'Logged in'])
        mock_imap.select.return_value = ('OK', [b'1'])
        mock_imap.search.return_value = ('OK', [b'1 2'])

        # Mock email data
        mock_imap.fetch.side_effect = [
            ('OK', [(b'1 (RFC822 {123}', b'From: test@example.com\r\nSubject: Test\r\n\r\nBody')]),
            ('OK', [(b'2 (RFC822 {123}', b'From: test2@example.com\r\nSubject: Test2\r\n\r\nBody2')])
        ]

        fetcher = EmailFetcher("imap.test.com", 993, "user", "pass")
        emails = fetcher.fetch_last_week()

        assert len(emails) == 2
        assert emails[0].sender == "test@example.com"
        assert emails[0].subject == "Test"
        assert "Body" in emails[0].body_text
