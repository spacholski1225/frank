# ABOUTME: Configuration loader for Telegram bot credentials and user authorization
# ABOUTME: Loads environment variables from .env file using python-dotenv

import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = os.getenv("ALLOWED_USER_ID")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in environment")

if not ALLOWED_USER_ID:
    raise ValueError("ALLOWED_USER_ID not set in environment")

ALLOWED_USER_ID = int(ALLOWED_USER_ID)
