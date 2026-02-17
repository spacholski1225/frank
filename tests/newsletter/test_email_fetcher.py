# ABOUTME: Unit tests for IMAP email fetching functionality
# ABOUTME: Tests connection, date filtering, and email data extraction

import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
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


class TestSenderWhitelist:
    def test_no_whitelist_allows_all(self):
        fetcher = EmailFetcher("imap.test.com", 993, "user", "pass")
        assert fetcher._is_allowed("anyone@example.com") is True

    def test_empty_whitelist_allows_all(self, tmp_path):
        senders_file = tmp_path / "senders.json"
        senders_file.write_text(json.dumps({"senders": []}))
        fetcher = EmailFetcher("imap.test.com", 993, "user", "pass", senders_file=senders_file)
        assert fetcher._is_allowed("anyone@example.com") is True

    def test_full_address_match(self, tmp_path):
        senders_file = tmp_path / "senders.json"
        senders_file.write_text(json.dumps({"senders": ["newsletter@tldr.tech"]}))
        fetcher = EmailFetcher("imap.test.com", 993, "user", "pass", senders_file=senders_file)
        assert fetcher._is_allowed("newsletter@tldr.tech") is True
        assert fetcher._is_allowed("other@tldr.tech") is False

    def test_domain_match(self, tmp_path):
        senders_file = tmp_path / "senders.json"
        senders_file.write_text(json.dumps({"senders": ["@bytebytego.com"]}))
        fetcher = EmailFetcher("imap.test.com", 993, "user", "pass", senders_file=senders_file)
        assert fetcher._is_allowed("news@bytebytego.com") is True
        assert fetcher._is_allowed("hello@bytebytego.com") is True
        assert fetcher._is_allowed("news@other.com") is False

    def test_case_insensitive_match(self, tmp_path):
        senders_file = tmp_path / "senders.json"
        senders_file.write_text(json.dumps({"senders": ["Newsletter@TLDR.tech"]}))
        fetcher = EmailFetcher("imap.test.com", 993, "user", "pass", senders_file=senders_file)
        assert fetcher._is_allowed("newsletter@tldr.tech") is True

    def test_missing_file_allows_all(self, tmp_path):
        senders_file = tmp_path / "nonexistent.json"
        fetcher = EmailFetcher("imap.test.com", 993, "user", "pass", senders_file=senders_file)
        assert fetcher._is_allowed("anyone@example.com") is True

    @patch('src.newsletter.email_fetcher.imaplib.IMAP4_SSL')
    def test_fetch_filters_by_whitelist(self, mock_imap_class, tmp_path):
        """Emails from non-whitelisted senders are excluded from results."""
        senders_file = tmp_path / "senders.json"
        senders_file.write_text(json.dumps({"senders": ["@allowed.com"]}))

        mock_imap = MagicMock()
        mock_imap_class.return_value = mock_imap
        mock_imap.login.return_value = ('OK', [b'Logged in'])
        mock_imap.select.return_value = ('OK', [b'1'])
        mock_imap.search.return_value = ('OK', [b'1 2'])
        mock_imap.fetch.side_effect = [
            ('OK', [(b'1 (RFC822 {123}', b'From: news@allowed.com\r\nSubject: Allowed\r\n\r\nBody')]),
            ('OK', [(b'2 (RFC822 {123}', b'From: spam@blocked.com\r\nSubject: Blocked\r\n\r\nBody')])
        ]

        fetcher = EmailFetcher("imap.test.com", 993, "user", "pass", senders_file=senders_file)
        emails = fetcher.fetch_last_week()

        assert len(emails) == 1
        assert "allowed.com" in emails[0].sender
