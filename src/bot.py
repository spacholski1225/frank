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
