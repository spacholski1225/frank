# ABOUTME: Configuration loader for Telegram bot credentials and user authorization
# ABOUTME: Loads environment variables from .env file using python-dotenv

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = os.getenv("ALLOWED_USER_ID")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in environment")

if not ALLOWED_USER_ID:
    raise ValueError("ALLOWED_USER_ID not set in environment")

ALLOWED_USER_ID = int(ALLOWED_USER_ID)

# Newsletter digest configuration
IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD")
NEWSLETTER_SCHEDULE_DAY = int(os.getenv("NEWSLETTER_SCHEDULE_DAY", "6"))
NEWSLETTER_SCHEDULE_HOUR = int(os.getenv("NEWSLETTER_SCHEDULE_HOUR", "20"))
NEWSLETTER_SCHEDULE_MINUTE = int(os.getenv("NEWSLETTER_SCHEDULE_MINUTE", "0"))

NEWSLETTER_SENDERS_FILE = Path(os.getenv("NEWSLETTER_SENDERS_FILE", str(Path(__file__).parent.parent / "senders.json")))

BLOG_SOURCES_FILE = Path(os.getenv("BLOG_SOURCES_FILE", str(Path(__file__).parent.parent / "blog_sources.json")))
BLOG_SCHEDULE_DAY = int(os.getenv("BLOG_SCHEDULE_DAY", "6"))
BLOG_SCHEDULE_HOUR = int(os.getenv("BLOG_SCHEDULE_HOUR", "21"))
BLOG_SCHEDULE_MINUTE = int(os.getenv("BLOG_SCHEDULE_MINUTE", "0"))
BLOG_ENABLED = BLOG_SOURCES_FILE.exists()

# IMAP config is optional (only needed for newsletter feature)
NEWSLETTER_ENABLED = bool(IMAP_HOST and IMAP_USER and IMAP_PASSWORD)

if IMAP_HOST and not IMAP_USER:
    raise ValueError("IMAP_HOST set but IMAP_USER missing")
if IMAP_HOST and not IMAP_PASSWORD:
    raise ValueError("IMAP_HOST set but IMAP_PASSWORD missing")
