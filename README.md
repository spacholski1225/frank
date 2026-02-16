# Claude-RPI Mobile Bridge

Telegram bot that enables mobile access to Claude Code running on Raspberry Pi (or any Linux host).

## Architecture

- **Python Bot**: Runs directly on host using aiogram to handle Telegram messages
- **Claude Code**: Installed natively on host, executed via subprocess
- **Communication**: Bot executes `claude -p "prompt"` directly

## Features

- Single-user authorization (whitelist by Telegram user ID)
- **Conversation continuity** - maintains conversation history across messages
- ANSI code removal for clean mobile output
- Automatic message splitting for long responses
- Direct execution on host (no Docker overhead)
- Full Claude Code features available
- `/new` command to start fresh conversation
- **Newsletter digest** - automated weekly email analysis and summaries (optional)

## Prerequisites

**Host system (RPI or Linux):**
- Python 3.11+
- Claude Code installed and logged in: `claude login`

## Installation

1. Clone repository:
```bash
git clone <repo-url>
cd claude-rpi-bridge
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
2. Send "Claude myśli..." status
3. Execute Claude Code with your message as prompt (continuing previous conversation)
4. Return cleaned response

**Starting fresh conversation:**
Send `/new` command to clear conversation history and start a new session.

## Newsletter Digest (Optional)

Automated weekly email digest:
- Fetches newsletters via IMAP every Sunday at 20:00
- Converts emails to Markdown format
- Analyzes content using Claude
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

2. Customize analysis in `.claude/prompts/newsletter_analysis_prompt.md`

3. Test locally:
```bash
python scripts/test_newsletter_digest.py --dry-run
```

**Storage:** Emails saved to `newsletters/[week]_[year]/`

## Testing

**Unit tests:**
```bash
source venv/bin/activate
pytest tests/ -v
```

**Integration test (requires Claude Code):**
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
3. Install Claude Code and login: `claude login`
4. Set up project:
```bash
cd claude-rpi-bridge
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your tokens
```

5. Run manually or set up as systemd service

**Setting up systemd service (auto-start on boot):**

Create `/etc/systemd/system/claude-bridge.service`:
```ini
[Unit]
Description=Claude RPI Telegram Bridge
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/claude-rpi-bridge
ExecStart=/home/YOUR_USERNAME/claude-rpi-bridge/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable claude-bridge
sudo systemctl start claude-bridge
```

**Monitoring:**
```bash
# View logs
sudo journalctl -u claude-bridge -f

# Restart service
sudo systemctl restart claude-bridge

# Check status
sudo systemctl status claude-bridge
```

**Updates:**
```bash
git pull
sudo systemctl restart claude-bridge
```

## Future Enhancements

- Multi-user support
- Command routing (`/status`, `/help`)
- Approval workflow for destructive commands
- File upload/download support

## License

MIT
