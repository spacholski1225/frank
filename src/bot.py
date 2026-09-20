# ABOUTME: Telegram bot message handler with user authorization and Codex execution
# ABOUTME: Receives messages, validates users, executes Codex prompts, returns formatted responses

import logging
import asyncio
from aiogram import types
from src.config import ALLOWED_USER_ID
from src.executor import execute_codex
from src.formatter import remove_ansi_codes, split_long_message
from src.session import get_session, save_session, clear_session

logger = logging.getLogger(__name__)

# Frank is single-user; serialize turns so concurrent messages cannot fork history.
_conversation_lock = asyncio.Lock()


def is_authorized(message: types.Message) -> bool:
    """Check if message sender is authorized."""
    return message.from_user.id == ALLOWED_USER_ID


async def handle_message(message: types.Message):
    """Handle incoming text messages."""
    if not is_authorized(message):
        await message.answer("Unauthorized")
        return

    # Send thinking status
    await message.answer("Frank myśli...")

    try:
        user_id = message.from_user.id
        prompt = message.text

        async with _conversation_lock:
            # Get existing session if any
            session_id = get_session(user_id)

            # Execute Codex with session continuity
            logger.info(f"Executing Codex with prompt: {prompt[:50]}...")
            result_text, new_session_id = await asyncio.to_thread(execute_codex, prompt, session_id)

            # Save new session ID for future messages
            if new_session_id:
                save_session(user_id, new_session_id)

        if not result_text:
            await message.answer("Error: Codex returned no output")
            return

        # Format and send response
        clean_output = remove_ansi_codes(result_text)
        chunks = split_long_message(clean_output)

        for chunk in chunks:
            await message.answer(chunk)

    except Exception as e:
        logger.error(f"Execution error: {e}", exc_info=True)
        await message.answer(f"Execution error: {str(e)}")


async def handle_new_command(message: types.Message):
    """Handle /new command to start fresh conversation."""
    if not is_authorized(message):
        await message.answer("Unauthorized")
        return

    user_id = message.from_user.id
    async with _conversation_lock:
        clear_session(user_id)
    await message.answer("Rozpoczynam nową konwersację. Historia została wyczyszczona.")
