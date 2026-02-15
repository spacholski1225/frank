# Claude-RPI Mobile Bridge Implementation Plan

> **For Claude:** Use `${CC_SKILLS_ROOT}/skills/collaboration/executing-plans/SKILL.md` to implement this plan task-by-task.

**Goal:** Build a Telegram bot that runs in Docker and executes Claude Code commands on the host system, enabling mobile AI assistant access.

**Architecture:** Docker container running Python/aiogram bot receives Telegram messages, validates user_id, executes `claude -p "prompt"` via subprocess with volume-mounted binary, formats output, and returns response to Telegram.

**Tech Stack:** Python 3.11, aiogram 3.15, Docker, docker-compose, pytest

---

## Task 1: Project Structure and Configuration

**Files:**
- Create: `src/__init__.py`
- Create: `src/config.py`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `.dockerignore`
- Create: `requirements.txt`

**Step 1: Create requirements.txt**

```txt
aiogram==3.15.0
python-dotenv==1.0.0
pytest==8.0.0
pytest-asyncio==0.23.0
```

**Step 2: Create .gitignore**

```
.env
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
*.log
```

**Step 3: Create .dockerignore**

```
.env
.git
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
*.log
README.md
docs/
tests/
```

**Step 4: Create .env.example**

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
ALLOWED_USER_ID=your_telegram_user_id
```

**Step 5: Create src/__init__.py**

Empty file (package marker).

**Step 6: Create src/config.py**

```python
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
```

**Step 7: Commit**

```bash
git add .gitignore .dockerignore .env.example requirements.txt src/__init__.py src/config.py
git commit -m "feat: add project structure and configuration

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Output Formatter (ANSI removal and message splitting)

**Files:**
- Create: `src/formatter.py`
- Create: `tests/test_formatter.py`

**Step 1: Write the failing test**

Create `tests/test_formatter.py`:

```python
import pytest
from src.formatter import remove_ansi_codes, split_long_message


def test_remove_ansi_codes_strips_color_codes():
    input_text = "\033[31mRed text\033[0m normal text"
    result = remove_ansi_codes(input_text)
    assert result == "Red text normal text"


def test_remove_ansi_codes_handles_plain_text():
    input_text = "Plain text without codes"
    result = remove_ansi_codes(input_text)
    assert result == "Plain text without codes"


def test_split_long_message_single_chunk():
    text = "Short message"
    result = split_long_message(text, max_length=4096)
    assert result == ["Short message"]


def test_split_long_message_multiple_chunks():
    text = "A" * 5000
    result = split_long_message(text, max_length=4096)
    assert len(result) == 2
    assert len(result[0]) == 4096
    assert len(result[1]) == 904
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_formatter.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.formatter'"

**Step 3: Write minimal implementation**

Create `src/formatter.py`:

```python
# ABOUTME: Output formatting utilities for cleaning Claude Code terminal output
# ABOUTME: Removes ANSI color codes and splits long messages for Telegram compatibility

import re


def remove_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from text."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def split_long_message(text: str, max_length: int = 4096) -> list[str]:
    """Split text into chunks that fit Telegram's message size limit."""
    if len(text) <= max_length:
        return [text]

    chunks = []
    while text:
        chunks.append(text[:max_length])
        text = text[max_length:]

    return chunks
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_formatter.py -v`
Expected: PASS (all 4 tests)

**Step 5: Commit**

```bash
git add src/formatter.py tests/test_formatter.py
git commit -m "feat: add output formatter with ANSI removal and message splitting

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Claude Executor (subprocess wrapper)

**Files:**
- Create: `src/executor.py`
- Create: `tests/test_executor.py`

**Step 1: Write the failing test**

Create `tests/test_executor.py`:

```python
import pytest
from unittest.mock import patch, MagicMock
from src.executor import execute_claude


@patch('src.executor.subprocess.run')
def test_execute_claude_success(mock_run):
    mock_run.return_value = MagicMock(
        stdout="Claude response",
        stderr="",
        returncode=0
    )

    stdout, stderr = execute_claude("test prompt")

    assert stdout == "Claude response"
    assert stderr == ""
    mock_run.assert_called_once_with(
        ["claude", "-p", "test prompt"],
        capture_output=True,
        text=True,
        timeout=None
    )


@patch('src.executor.subprocess.run')
def test_execute_claude_with_stderr(mock_run):
    mock_run.return_value = MagicMock(
        stdout="Output",
        stderr="Warning message",
        returncode=0
    )

    stdout, stderr = execute_claude("prompt")

    assert stdout == "Output"
    assert stderr == "Warning message"


@patch('src.executor.subprocess.run')
def test_execute_claude_command_not_found(mock_run):
    mock_run.side_effect = FileNotFoundError("claude: command not found")

    with pytest.raises(FileNotFoundError):
        execute_claude("prompt")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_executor.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.executor'"

**Step 3: Write minimal implementation**

Create `src/executor.py`:

```python
# ABOUTME: Claude Code execution wrapper for running AI prompts via subprocess
# ABOUTME: Handles subprocess calls to native Claude binary with error handling

import subprocess


def execute_claude(prompt: str) -> tuple[str, str]:
    """
    Execute Claude Code with given prompt.

    Args:
        prompt: User prompt to send to Claude

    Returns:
        Tuple of (stdout, stderr)

    Raises:
        FileNotFoundError: If claude binary not found
        subprocess.CalledProcessError: If claude execution fails
    """
    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=None
    )

    return result.stdout, result.stderr
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_executor.py -v`
Expected: PASS (all 3 tests)

**Step 5: Commit**

```bash
git add src/executor.py tests/test_executor.py
git commit -m "feat: add Claude executor with subprocess wrapper

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Telegram Bot Handler

**Files:**
- Create: `src/bot.py`
- Create: `tests/test_bot.py`

**Step 1: Write the failing test**

Create `tests/test_bot.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.bot import is_authorized, handle_message


def test_is_authorized_valid_user():
    with patch('src.bot.ALLOWED_USER_ID', 12345):
        message = MagicMock()
        message.from_user.id = 12345
        assert is_authorized(message) is True


def test_is_authorized_invalid_user():
    with patch('src.bot.ALLOWED_USER_ID', 12345):
        message = MagicMock()
        message.from_user.id = 99999
        assert is_authorized(message) is False


@pytest.mark.asyncio
async def test_handle_message_unauthorized():
    with patch('src.bot.ALLOWED_USER_ID', 12345):
        message = AsyncMock()
        message.from_user.id = 99999
        message.text = "test"

        await handle_message(message)

        message.answer.assert_called_once_with("Unauthorized")


@pytest.mark.asyncio
@patch('src.bot.execute_claude')
@patch('src.bot.remove_ansi_codes')
@patch('src.bot.split_long_message')
async def test_handle_message_success(mock_split, mock_remove_ansi, mock_execute):
    with patch('src.bot.ALLOWED_USER_ID', 12345):
        mock_execute.return_value = ("Claude output", "")
        mock_remove_ansi.return_value = "Clean output"
        mock_split.return_value = ["Clean output"]

        message = AsyncMock()
        message.from_user.id = 12345
        message.text = "test prompt"

        await handle_message(message)

        # Verify thinking message sent
        assert message.answer.call_count == 2
        first_call = message.answer.call_args_list[0]
        assert "Claude myśli" in first_call[0][0]

        # Verify result sent
        second_call = message.answer.call_args_list[1]
        assert second_call[0][0] == "Clean output"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_bot.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.bot'"

**Step 3: Write minimal implementation**

Create `src/bot.py`:

```python
# ABOUTME: Telegram bot message handler with user authorization and Claude execution
# ABOUTME: Receives messages, validates users, executes Claude prompts, returns formatted responses

from aiogram import types
from src.config import ALLOWED_USER_ID
from src.executor import execute_claude
from src.formatter import remove_ansi_codes, split_long_message


def is_authorized(message: types.Message) -> bool:
    """Check if message sender is authorized."""
    return message.from_user.id == ALLOWED_USER_ID


async def handle_message(message: types.Message):
    """Handle incoming text messages."""
    if not is_authorized(message):
        await message.answer("Unauthorized")
        return

    # Send thinking status
    await message.answer("Claude myśli...")

    # Execute Claude
    prompt = message.text
    stdout, stderr = execute_claude(prompt)

    # Format output
    output = stdout if stdout else stderr
    clean_output = remove_ansi_codes(output)
    chunks = split_long_message(clean_output)

    # Send response
    for chunk in chunks:
        await message.answer(chunk)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_bot.py -v`
Expected: PASS (all 4 tests)

**Step 5: Commit**

```bash
git add src/bot.py tests/test_bot.py
git commit -m "feat: add Telegram bot handler with authorization

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Main Entry Point

**Files:**
- Create: `main.py`

**Step 1: Write main.py**

```python
# ABOUTME: Main entry point for Claude-RPI Telegram bridge bot
# ABOUTME: Initializes aiogram bot and dispatcher, registers handlers, starts polling

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram import F

from src.config import TELEGRAM_BOT_TOKEN
from src.bot import handle_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Initialize and start the bot."""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    # Register message handler for all text messages
    dp.message.register(handle_message, F.text)

    logger.info("Starting Claude-RPI Bridge bot...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
```

**Step 2: Test manually (requires .env with valid tokens)**

Create `.env` file with:
```
TELEGRAM_BOT_TOKEN=your_actual_token
ALLOWED_USER_ID=your_actual_id
```

Run: `python main.py`
Expected: Bot starts, logs "Starting Claude-RPI Bridge bot..."

**Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add main entry point for bot

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Docker Configuration

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`

**Step 1: Create Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY main.py .

# Run bot
CMD ["python", "main.py"]
```

**Step 2: Create docker-compose.yml**

```yaml
version: '3.8'

services:
  claude-bridge:
    build: .
    container_name: claude-bridge
    restart: always
    env_file: .env
    volumes:
      - /usr/local/bin/claude:/usr/local/bin/claude:ro
      - ~/.claude:/root/.claude:ro
      - /home/spacholski:/home/spacholski
      - /tmp:/tmp
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Step 3: Test Docker build**

Run: `docker-compose build`
Expected: Build succeeds without errors

**Step 4: Commit**

```bash
git add Dockerfile docker-compose.yml
git commit -m "feat: add Docker configuration

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Integration Test (requires Claude Code on host)

**Files:**
- Create: `tests/test_integration.py`

**Step 1: Write integration test**

Create `tests/test_integration.py`:

```python
import pytest
from src.executor import execute_claude
from src.formatter import remove_ansi_codes


@pytest.mark.integration
def test_real_claude_execution():
    """
    Integration test - requires Claude Code installed and logged in.
    Run with: pytest tests/test_integration.py -v -m integration
    """
    prompt = "Say 'hello' and nothing else"

    stdout, stderr = execute_claude(prompt)

    # Verify we got output
    assert stdout or stderr

    # Clean output
    clean = remove_ansi_codes(stdout if stdout else stderr)

    # Verify output is non-empty
    assert len(clean.strip()) > 0
```

**Step 2: Mark integration tests in pytest.ini**

Create `pytest.ini`:

```ini
[pytest]
markers =
    integration: marks tests as integration tests (require Claude Code installed)
```

**Step 3: Run integration test (skip if Claude not installed)**

Run: `pytest tests/test_integration.py -v -m integration`

Expected:
- If Claude installed: PASS
- If Claude not installed: FAIL with FileNotFoundError (expected)

**Step 4: Commit**

```bash
git add tests/test_integration.py pytest.ini
git commit -m "test: add integration test for Claude execution

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Documentation

**Files:**
- Create: `README.md`

**Step 1: Create README.md**

```markdown
# Claude-RPI Mobile Bridge

Telegram bot that enables mobile access to Claude Code running on Raspberry Pi (or any Linux host).

## Architecture

- **Docker Container**: Runs Python bot (aiogram) that handles Telegram messages
- **Host System**: Claude Code installed natively, accessed via volume mount
- **Communication**: Bot executes `claude -p "prompt` via subprocess

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
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive README

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Final Verification

**Step 1: Run all tests**

```bash
pytest tests/ -v
```

Expected: All unit tests pass (integration test skipped unless marked)

**Step 2: Verify Docker build**

```bash
docker-compose build
```

Expected: Clean build

**Step 3: Manual test (if tokens available)**

```bash
docker-compose up
# Send message from Telegram
# Verify bot responds
```

**Step 4: Final commit and tag**

```bash
git tag v1.0.0-mvp
git log --oneline -10
```

---

## Plan Complete

**Implementation order:**
1. Project structure and config
2. Formatter (ANSI + splitting)
3. Executor (subprocess wrapper)
4. Bot handler (Telegram logic)
5. Main entry point
6. Docker configuration
7. Integration test
8. Documentation

**Key principles applied:**
- **TDD**: Tests before implementation (Tasks 2-4)
- **DRY**: Reusable formatter and executor modules
- **YAGNI**: No MCP, no multi-user, no streaming (MVP only)
- **Frequent commits**: After each task completion

**Testing strategy:**
- Unit tests with mocks (executor, formatter, bot)
- Integration test for real Claude execution
- Manual testing with Docker

**Total estimated time:** 1-2 hours for experienced developer with zero context.
