#!/usr/bin/env python3
# ABOUTME: Generates fake newsletter emails for testing
# ABOUTME: Creates realistic test data without needing real IMAP connection

"""
Test Email Generator

Usage:
  python scripts/create_test_emails.py
  python scripts/create_test_emails.py --count 5
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.newsletter.email_converter import EmailConverter
from src.newsletter.email_fetcher import EmailData


SAMPLE_NEWSLETTERS = [
    {
        "sender": "newsletter@github.com",
        "subject": "GitHub Changelog - February Edition",
        "html": """
        <h1>GitHub Changelog</h1>
        <h2>New Features</h2>
        <ul>
            <li><a href="https://github.blog/feature1">Copilot Enterprise now available</a></li>
            <li>GitHub Actions: New caching improvements</li>
            <li>Security: Dependabot alerts enhanced</li>
        </ul>
        <h2>Bug Fixes</h2>
        <p>Various improvements to GitHub Pages deployment.</p>
        """
    },
    {
        "sender": "weekly@pythonweekly.com",
        "subject": "Python Weekly - Issue 634",
        "html": """
        <h1>Python Weekly</h1>
        <h2>Articles</h2>
        <ul>
            <li><a href="https://example.com/async">Understanding AsyncIO internals</a></li>
            <li><a href="https://example.com/performance">Python 3.13 Performance Benchmarks</a></li>
        </ul>
        <h2>Projects</h2>
        <ul>
            <li><strong>FastAPI 0.110.0</strong> - New validation features</li>
            <li><strong>Pydantic V2</strong> - Migration guide available</li>
        </ul>
        """
    },
    {
        "sender": "news@hackernewsletter.com",
        "subject": "Hacker Newsletter #650",
        "html": """
        <h1>Top Stories This Week</h1>
        <ol>
            <li><a href="https://news.ycombinator.com/1">Show HN: I built a self-hosting AI assistant</a></li>
            <li><a href="https://news.ycombinator.com/2">The state of WebAssembly in 2026</a></li>
            <li><a href="https://news.ycombinator.com/3">PostgreSQL 17 released with major performance improvements</a></li>
        </ol>
        """
    },
    {
        "sender": "security@owasp.org",
        "subject": "OWASP Security Advisory - CVE-2026-12345",
        "html": """
        <h1>Security Advisory</h1>
        <p><strong>Severity: HIGH</strong></p>
        <h2>Affected Packages</h2>
        <ul>
            <li>django &lt; 5.0.3</li>
            <li>requests &lt; 2.31.1</li>
        </ul>
        <h2>Mitigation</h2>
        <p>Update to latest versions immediately. See <a href="https://owasp.org/advisory">full advisory</a>.</p>
        """
    },
    {
        "sender": "events@pycon.org",
        "subject": "PyCon US 2026 - CFP Open",
        "html": """
        <h1>PyCon US 2026</h1>
        <p><strong>Dates:</strong> May 15-23, 2026<br>
        <strong>Location:</strong> Pittsburgh, PA</p>
        <h2>Call for Proposals</h2>
        <p>CFP deadline: March 1, 2026</p>
        <p>We're looking for talks on:</p>
        <ul>
            <li>AI/ML applications</li>
            <li>Web frameworks</li>
            <li>Testing and DevOps</li>
        </ul>
        <p><a href="https://pycon.org/cfp">Submit your proposal</a></p>
        """
    }
]


def parse_args():
    parser = argparse.ArgumentParser(description='Generate test newsletter emails')
    parser.add_argument('--count', type=int, default=3, help='Number of emails to generate (max 5)')
    return parser.parse_args()


def main():
    args = parse_args()
    count = min(args.count, len(SAMPLE_NEWSLETTERS))

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"newsletters/test_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {count} test emails in {output_dir}")

    converter = EmailConverter()

    # Generate emails
    for i in range(count):
        sample = SAMPLE_NEWSLETTERS[i]

        # Create EmailData
        email_data = EmailData(
            sender=sample["sender"],
            subject=sample["subject"],
            date=datetime.now() - timedelta(days=random.randint(0, 6)),
            body_text="",  # Will use HTML
            body_html=sample["html"],
            message_id=f"<test{i}@example.com>"
        )

        # Convert to Markdown
        markdown = converter.to_markdown(email_data)
        filename = converter.generate_filename(email_data, sequence=i+1)

        # Save
        file_path = output_dir / filename
        file_path.write_text(markdown, encoding='utf-8')

        print(f"  ✓ {filename}")

    print(f"\n✅ Generated {count} test emails")
    print(f"📁 Location: {output_dir}")
    print(f"\nNext steps:")
    print(f"  1. Test Claude analysis:")
    print(f"     python scripts/test_newsletter_digest.py --skip-fetch --dry-run")
    print(f"  2. Or manually run Claude:")
    print(f"     claude -p \"$(cat .claude/prompts/newsletter_analysis_prompt.md)\" --allowedTools Read,Glob,Write")


if __name__ == "__main__":
    main()
