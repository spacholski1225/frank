# Frank — Codex Telegram Agent

Telegram bot that enables mobile access to Codex CLI running on Raspberry Pi (or any Linux host).

## Architecture

- **Python Bot**: Runs directly on host using aiogram to handle Telegram messages
- **Codex CLI**: Installed natively on host, executed via subprocess
- **Communication**: Bot executes `codex exec --json` directly

## Features

- Single-user authorization (whitelist by Telegram user ID)
- **Conversation continuity** - maintains conversation history across messages
- ANSI code removal for clean mobile output
- Automatic message splitting for long responses
- Direct execution on host (no Docker overhead)
- Read-only Codex execution; live web search for blog collection
- `/new` command to start fresh conversation
- **Newsletter digest** - automated weekly email analysis and summaries (optional)

## Prerequisites

**Host system (RPI or Linux):**
- Python 3.11+
- Codex CLI installed and logged in: `codex login`

## Installation

1. Clone repository:
```bash
git clone <repo-url>
cd frank
```

2. Create virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Telegram bot token and user ID
```

4. Run the bot:
```bash
./run-local.sh
```

## Usage

**Regular messages:**
Send any text message to your Telegram bot. The bot will:
1. Verify you're authorized (by user ID)
2. Send "Frank myśli..." status
3. Execute Codex CLI with your message as prompt (continuing previous conversation)
4. Return cleaned response

**Starting fresh conversation:**
Send `/new` command to clear conversation history and start a new session.

## Newsletter Digest (Optional)

Automated weekly email digest:
- Fetches newsletters via IMAP every Sunday at 20:00
- Converts emails to Markdown format
- Analyzes content using Codex
- Sends summary to Telegram

**Setup:**
1. Add IMAP credentials to `.env`:
```bash
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USER=your@email.com
IMAP_PASSWORD=app_password  # Use app-specific password
NEWSLETTER_SCHEDULE_DAY=6   # 0=Mon, 6=Sun
NEWSLETTER_SCHEDULE_HOUR=20
```

2. Customize analysis in `prompts/newsletter_analysis_prompt.md`

3. Test locally:
```bash
python scripts/test_newsletter_digest.py --dry-run
```

**Storage:** Emails saved to `newsletters/[week]_[year]/`

## Testing

**Unit tests:**
```bash
source venv/bin/activate
pytest tests/ -v -m "not integration"
```

**Integration test (requires Codex CLI):**
```bash
pytest tests/test_integration.py -v -m integration
```

## Development

**Running manually:**
```bash
source venv/bin/activate
python main.py
```

## Deployment on RPI

1. Transfer code: `git clone` on RPI
2. Install Python 3.11+: `sudo apt install python3 python3-venv python3-pip`
3. Install Codex CLI and login: `codex login`
4. Set up project:
```bash
cd frank
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your tokens
```

5. Run manually or set up as systemd service

**Setting up systemd service (auto-start on boot):**

Create `/etc/systemd/system/frank.service`:
```ini
[Unit]
Description=Frank Codex Telegram Agent
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/frank
ExecStart=/home/YOUR_USERNAME/frank/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable frank
sudo systemctl start frank
```

**Monitoring:**
```bash
# View logs
sudo journalctl -u frank -f

# Restart service
sudo systemctl restart frank

# Check status
sudo systemctl status frank
```

**Updates:**
```bash
git pull
sudo systemctl restart frank
```

## Future Enhancements

- Multi-user support
- Command routing (`/status`, `/help`)
- Approval workflow for destructive commands
- File upload/download support

## License

MIT


## Codex migration

Install Codex CLI on the machine running Frank, then run `codex login` as the
same OS user that runs the bot. Check `codex login status` before starting Frank.
Use a current CLI with `codex exec --json --output-last-message` and `exec resume`.
Official setup: https://learn.chatgpt.com/docs/codex/cli

Optional `.env` settings:

```dotenv
CODEX_BIN=codex
# CODEX_MODEL=your-model-id
CODEX_TIMEOUT=600
```

If a background service cannot find Codex, set CODEX_BIN to its absolute path.
Chat, newsletter analysis, blog collection and blog summaries now use Codex.
Existing IMAP settings, senders.json, blog_sources.json and weekly schedules remain.
Old Claude conversation IDs cannot be resumed in Codex; start a new conversation.

Reports keep the existing Polish content filters and sections. Editable templates
are in `prompts/`. Codex returns the report; Python writes `summary.md`, avoiding
stale output. Blog inputs are archived in a separate `run-*` folder for each run,
with the latest successful weekly report also in the parent folder. Failed sources
are reported instead of silently becoming “no news”.

Codex runs read-only with no interactive approval prompts. Blog collection enables
live web search; newsletter and aggregate analysis disable web search. File access
still follows the host's Codex configuration. The Claude `.mcp.json` is not imported
by this migration; Google Calendar is outside the email/blog migration scope.

Verification without sending Telegram messages:

```bash
python -m pytest tests/ -m "not integration"
python scripts/test_newsletter_digest.py --dry-run
python scripts/test_blog_digest.py --dry-run
```

The two digest commands use live sources and Codex. Unit tests mock those services.
To summarize a saved email folder without IMAP or Telegram:

```bash
python scripts/summarize_saved.py newsletter /absolute/path/to/emails
python scripts/summarize_saved.py blog /absolute/path/to/blog-markdown
```
