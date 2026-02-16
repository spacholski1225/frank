# ABOUTME: Unit tests for email HTML to Markdown conversion
# ABOUTME: Tests conversion, metadata extraction, and file naming

from datetime import datetime
from src.newsletter.email_converter import EmailConverter
from src.newsletter.email_fetcher import EmailData


class TestEmailConverter:
    def test_convert_html_to_markdown(self):
        """Test HTML email conversion to Markdown."""
        email_data = EmailData(
            sender="newsletter@github.com",
            subject="GitHub Changelog Feb 10",
            date=datetime(2026, 2, 10, 14, 23, 0),
            body_text="Plain text version",
            body_html="<h1>Title</h1><p>Content with <a href='https://example.com'>link</a></p>",
            message_id="<unique@github.com>"
        )

        converter = EmailConverter()
        markdown = converter.to_markdown(email_data)

        # Check frontmatter
        assert "---" in markdown
        assert "from: newsletter@github.com" in markdown
        assert "subject: GitHub Changelog Feb 10" in markdown
        assert "date: 2026-02-10" in markdown

        # Check content conversion
        assert "# Title" in markdown
        assert "[link](https://example.com)" in markdown

    def test_generate_filename(self):
        """Test filename generation from email metadata."""
        email_data = EmailData(
            sender="newsletter@github.com",
            subject="GitHub Changelog Feb 10!",
            date=datetime(2026, 2, 10),
            body_text="",
            body_html="",
            message_id=""
        )

        converter = EmailConverter()
        filename = converter.generate_filename(email_data, sequence=5)

        assert filename == "005_github.com_github-changelog-feb-10.md"
