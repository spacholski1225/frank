# ABOUTME: Converts email data to Markdown format with metadata
# ABOUTME: Handles HTML to Markdown conversion and filename generation

import html2text
import re
from src.newsletter.email_fetcher import EmailData


class EmailConverter:
    """Converts emails to Markdown format."""

    def __init__(self):
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.body_width = 0  # Don't wrap lines

    def to_markdown(self, email: EmailData) -> str:
        """Convert email to Markdown with frontmatter."""
        # Convert HTML to Markdown if available, otherwise use plain text
        if email.body_html:
            content = self.html_converter.handle(email.body_html)
        else:
            content = email.body_text

        # Build frontmatter
        frontmatter = f"""---
from: {email.sender}
subject: {email.subject}
date: {email.date.strftime('%Y-%m-%d %H:%M:%S')}
message_id: {email.message_id}
---

"""

        return frontmatter + content

    def generate_filename(self, email: EmailData, sequence: int) -> str:
        """Generate filename from email metadata.

        Format: {seq:03d}_{sender_domain}_{subject_slug}.md
        Example: 001_github.com_github-changelog-feb-10.md
        """
        # Extract domain from sender
        sender_match = re.search(r'@([\w\.-]+)', email.sender)
        sender_domain = sender_match.group(1) if sender_match else 'unknown'

        # Create slug from subject
        subject_slug = email.subject.lower()
        subject_slug = re.sub(r'[^\w\s-]', '', subject_slug)  # Remove special chars
        subject_slug = re.sub(r'[\s_]+', '-', subject_slug)    # Replace spaces with -
        subject_slug = subject_slug[:50]                        # Max 50 chars
        subject_slug = subject_slug.strip('-')                  # Remove leading/trailing -

        return f"{sequence:03d}_{sender_domain}_{subject_slug}.md"
