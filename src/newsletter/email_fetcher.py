# ABOUTME: IMAP email fetcher for newsletter digest
# ABOUTME: Connects to IMAP server, fetches emails from last 7 days, extracts metadata and content

import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List
import logging

logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    """Email metadata and content."""
    sender: str
    subject: str
    date: datetime
    body_text: str
    body_html: str
    message_id: str


class EmailFetcher:
    """Fetches emails from IMAP server."""

    def __init__(self, host: str, port: int, user: str, password: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def fetch_last_week(self) -> List[EmailData]:
        """Fetch all emails from the last 7 days."""
        emails = []

        try:
            # Connect to IMAP server
            imap = imaplib.IMAP4_SSL(self.host, self.port)
            imap.login(self.user, self.password)
            imap.select('INBOX')

            # Calculate date 7 days ago
            since_date = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")

            # Search for emails since that date
            status, messages = imap.search(None, f'(SINCE {since_date})')

            if status != 'OK':
                logger.error("Failed to search emails")
                return emails

            email_ids = messages[0].split()

            for email_id in email_ids:
                status, msg_data = imap.fetch(email_id, '(RFC822)')

                if status != 'OK':
                    logger.warning(f"Failed to fetch email {email_id}")
                    continue

                # Parse email
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                # Extract metadata
                subject = self._decode_header(msg.get('Subject', ''))
                sender = self._decode_header(msg.get('From', ''))
                date_str = msg.get('Date', '')
                message_id = msg.get('Message-ID', '')

                # Parse date
                try:
                    date = email.utils.parsedate_to_datetime(date_str)
                except:
                    date = datetime.now()

                # Extract body
                body_text, body_html = self._extract_body(msg)

                emails.append(EmailData(
                    sender=sender,
                    subject=subject,
                    date=date,
                    body_text=body_text,
                    body_html=body_html,
                    message_id=message_id
                ))

            imap.close()
            imap.logout()

        except Exception as e:
            logger.error(f"IMAP error: {e}", exc_info=True)
            raise

        return emails

    def _decode_header(self, header: str) -> str:
        """Decode email header handling encoding."""
        if not header:
            return ""

        decoded_parts = decode_header(header)
        result = []

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                result.append(part.decode(encoding or 'utf-8', errors='replace'))
            else:
                result.append(part)

        return ''.join(result)

    def _extract_body(self, msg) -> tuple[str, str]:
        """Extract text and HTML body from email."""
        body_text = ""
        body_html = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()

                if content_type == 'text/plain':
                    try:
                        body_text = part.get_payload(decode=True).decode('utf-8', errors='replace')
                    except:
                        pass
                elif content_type == 'text/html':
                    try:
                        body_html = part.get_payload(decode=True).decode('utf-8', errors='replace')
                    except:
                        pass
        else:
            try:
                body_text = msg.get_payload(decode=True).decode('utf-8', errors='replace')
            except:
                body_text = str(msg.get_payload())

        return body_text, body_html
