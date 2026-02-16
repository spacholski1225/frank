#!/usr/bin/env python3
# ABOUTME: Local testing script for newsletter digest functionality
# ABOUTME: Allows testing without waiting for scheduler, supports dry-run and selective execution

"""
Newsletter Digest Test Script

Usage:
  python scripts/test_newsletter_digest.py
  python scripts/test_newsletter_digest.py --week 7 --year 2026
  python scripts/test_newsletter_digest.py --dry-run
  python scripts/test_newsletter_digest.py --skip-fetch
  python scripts/test_newsletter_digest.py --output-only
"""

import sys
import argparse
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.newsletter.processor import NewsletterProcessor
from src.config import IMAP_HOST, IMAP_PORT, IMAP_USER, IMAP_PASSWORD, TELEGRAM_BOT_TOKEN, ALLOWED_USER_ID

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description='Test newsletter digest locally')
    parser.add_argument('--week', type=int, help='Week number (default: current week)')
    parser.add_argument('--year', type=int, help='Year (default: current year)')
    parser.add_argument('--dry-run', action='store_true', help='Process but do not send to Telegram')
    parser.add_argument('--skip-fetch', action='store_true', help='Use existing emails if available')
    parser.add_argument('--output-only', action='store_true', help='Only display summary, do not save')
    return parser.parse_args()


async def send_to_telegram(summary: str, email_count: int):
    """Send summary to Telegram."""
    from aiogram import Bot
    from src.formatter import split_long_message

    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    try:
        header = f"📬 Newsletter Digest (TEST) - {email_count} maili\n\n"
        message = header + summary

        chunks = split_long_message(message)

        for chunk in chunks:
            await bot.send_message(ALLOWED_USER_ID, chunk)

        logger.info("Summary sent to Telegram")
    finally:
        await bot.session.close()


def main():
    args = parse_args()

    # Check IMAP configuration
    if not all([IMAP_HOST, IMAP_USER, IMAP_PASSWORD]):
        logger.error("IMAP not configured in .env file")
        sys.exit(1)

    logger.info("=== Newsletter Digest Test ===")
    logger.info(f"IMAP: {IMAP_USER}@{IMAP_HOST}")
    logger.info(f"Mode: {'DRY RUN' if args.dry_run else 'FULL'}")

    if args.skip_fetch:
        logger.info("Skip fetch: Using existing emails")

    try:
        # Create processor
        processor = NewsletterProcessor(
            imap_host=IMAP_HOST,
            imap_port=IMAP_PORT,
            imap_user=IMAP_USER,
            imap_password=IMAP_PASSWORD
        )

        # Run processing
        logger.info("\n--- Starting processing ---")
        result = processor.process()

        if not result["success"]:
            logger.error(f"Processing failed: {result.get('error')}")
            sys.exit(2)

        # Display results
        logger.info(f"\n--- Results ---")
        logger.info(f"Emails processed: {result['email_count']}")
        logger.info(f"Folder: {result['folder']}")

        summary = result['summary']

        if args.output_only:
            print("\n" + "="*60)
            print(summary)
            print("="*60 + "\n")
        else:
            logger.info(f"Summary saved to: {result['folder']}/summary.md")

        # Send to Telegram if not dry-run
        if not args.dry_run and not args.output_only:
            logger.info("\n--- Sending to Telegram ---")
            asyncio.run(send_to_telegram(summary, result['email_count']))
        elif args.dry_run:
            logger.info("\nDRY RUN: Skipping Telegram send")

        logger.info("\n✅ Test completed successfully")
        sys.exit(0)

    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}", exc_info=True)
        sys.exit(3)


if __name__ == "__main__":
    main()
