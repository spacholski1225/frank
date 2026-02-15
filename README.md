# Claude-RPI Mobile Bridge

Telegram bot that enables mobile access to Claude Code running on Raspberry Pi (or any Linux host).

## Architecture

- **Docker Container**: Runs Python bot (aiogram) that handles Telegram messages
- **Host System**: Claude Code installed natively, accessed via volume mount
- **Communication**: Bot executes `claude -p "prompt" --yes` via subprocess

## Features

- Single-user authorization (whitelist by Telegram user ID)
- ANSI code removal for clean mobile output
- Automatic message splitting for long responses
- Docker-based deployment with auto-restart
- Full filesystem access for Claude (reads/writes host files)

## Prerequisites

**Host system (RPI or Linux):**
- Docker + docker-compose
- Claude Code installed: `claude login`

## Installation

1. Clone repository:
```bash
git clone <repo-url>
cd claude-rpi-bridge
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Telegram bot token and user ID
```

3. Build and run:
```bash
docker-compose up -d
```

4. Check logs:
```bash
docker logs -f claude-bridge
```

## Usage

Send any text message to your Telegram bot. The bot will:
1. Verify you're authorized (by user ID)
2. Send "Claude myśli..." status
3. Execute Claude Code with your message as prompt
4. Return cleaned response

## Testing

**Unit tests:**
```bash
pytest tests/ -v
```

**Integration test (requires Claude Code):**
```bash
pytest tests/test_integration.py -v -m integration
```

## Development

**Local testing without Docker:**
```bash
pip install -r requirements.txt
python main.py
```

## Deployment

**RPI deployment:**
1. Transfer code: `git clone` on RPI
2. Install Docker: `curl -fsSL https://get.docker.com | sh`
3. Install Claude Code and login
4. Configure `.env`
5. Run: `docker-compose up -d`

**Updates:**
```bash
git pull
docker-compose build
docker-compose up -d
```

## Monitoring

**Logs:**
```bash
docker logs -f claude-bridge
docker logs --tail 100 claude-bridge
```

**Restart:**
```bash
docker-compose restart
```

## Future Enhancements

- MCP server integration (add to `~/.claude/config.json`)
- Multi-user support
- Command routing (`/status`, `/help`)
- Response streaming
- Approval workflow for destructive commands

## License

MIT
