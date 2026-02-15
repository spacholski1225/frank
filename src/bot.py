# ABOUTME: Telegram bot message handler with user authorization and Claude execution
# ABOUTME: Receives messages, validates users, executes Claude prompts, returns formatted responses

import logging
from aiogram import types
from src.config import ALLOWED_USER_ID
from src.executor import execute_claude
from src.formatter import remove_ansi_codes, split_long_message

logger = logging.getLogger(__name__)


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

    try:
        # Execute Claude
        prompt = message.text
        logger.info(f"Executing Claude with prompt: {prompt[:50]}...")
        stdout, stderr = execute_claude(prompt)

        logger.info(f"Claude stdout length: {len(stdout)}")
        logger.info(f"Claude stderr length: {len(stderr)}")
        logger.info(f"Claude stdout content: {repr(stdout)}")
        if stderr:
            logger.info(f"Claude stderr content: {repr(stderr)}")

        if stderr:
            logger.warning(f"Claude stderr: {stderr}")

        # Format output
        output = stdout if stdout else stderr

        if not output:
            await message.answer("Error: Claude returned no output")
            return

        clean_output = remove_ansi_codes(output)
        chunks = split_long_message(clean_output)

        # Send response
        for chunk in chunks:
            await message.answer(chunk)

    except Exception as e:
        logger.error(f"Execution error: {e}", exc_info=True)
        await message.answer(f"Execution error: {str(e)}")
