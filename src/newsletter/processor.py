# ABOUTME: Orchestrates newsletter processing pipeline
# ABOUTME: Coordinates email fetching, conversion, storage, and Claude analysis

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from src.newsletter.email_fetcher import EmailFetcher
from src.newsletter.email_converter import EmailConverter
from src.newsletter.claude_runner import ClaudeRunner

logger = logging.getLogger(__name__)


class NewsletterProcessor:
    """Orchestrates the newsletter digest pipeline."""

    def __init__(self, imap_host: str, imap_port: int, imap_user: str, imap_password: str, senders_file: Path = None):
        self.fetcher = EmailFetcher(imap_host, imap_port, imap_user, imap_password, senders_file=senders_file)
        self.converter = EmailConverter()
        self.runner = ClaudeRunner()
        self.base_dir = Path("newsletters")

    def process(self) -> Dict[str, Any]:
        """
        Run complete newsletter processing pipeline.

        Returns:
            Dict with processing results:
            {
                "success": bool,
                "email_count": int,
                "folder": str,
                "summary": str,
                "error": str (if failed)
            }
        """
        try:
            # Step 1: Fetch emails
            logger.info("Fetching emails from last week...")
            emails = self.fetcher.fetch_last_week()

            if not emails:
                logger.info("No emails found in last week")
                return {
                    "success": True,
                    "email_count": 0,
                    "folder": None,
                    "summary": "No newsletters received this week."
                }

            logger.info(f"Fetched {len(emails)} emails")

            # Step 2: Create output folder
            week_num = datetime.now().isocalendar()[1]
            year = datetime.now().year
            folder_name = f"{week_num:02d}_{year}"
            output_dir = self.base_dir / folder_name
            output_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Saving emails to {output_dir}")

            # Step 3: Convert and save emails
            for idx, email_data in enumerate(emails, start=1):
                markdown = self.converter.to_markdown(email_data)
                filename = self.converter.generate_filename(email_data, sequence=idx)

                file_path = output_dir / filename
                file_path.write_text(markdown, encoding='utf-8')
                logger.debug(f"Saved {filename}")

            # Step 4: Save metadata
            metadata = {
                "processed_at": datetime.now().isoformat(),
                "email_count": len(emails),
                "week": week_num,
                "year": year
            }

            metadata_path = output_dir / "_metadata.json"
            metadata_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')

            # Step 5: Run Claude analysis
            logger.info("Running Claude analysis...")
            analysis_output = self.runner.analyze_newsletters(str(output_dir))

            # Step 6: Read generated summary
            summary_path = output_dir / "summary.md"

            if summary_path.exists():
                summary = summary_path.read_text(encoding='utf-8')
            else:
                logger.warning("summary.md not found, using Claude stdout")
                summary = analysis_output

            logger.info("Newsletter processing completed successfully")

            return {
                "success": True,
                "email_count": len(emails),
                "folder": str(output_dir),
                "summary": summary
            }

        except Exception as e:
            logger.error(f"Newsletter processing failed: {e}", exc_info=True)
            return {
                "success": False,
                "email_count": 0,
                "folder": None,
                "summary": None,
                "error": str(e)
            }
