import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock

# Set required env vars before importing modules
os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
os.environ['ALLOWED_USER_ID'] = '12345'

from src.bot import is_authorized, handle_message, handle_new_command


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
@patch('src.bot.get_session')
@patch('src.bot.save_session')
@patch('src.bot.execute_claude')
@patch('src.bot.remove_ansi_codes')
@patch('src.bot.split_long_message')
async def test_handle_message_success_no_session(mock_split, mock_remove_ansi, mock_execute, mock_save, mock_get):
    with patch('src.bot.ALLOWED_USER_ID', 12345):
        mock_get.return_value = None
        mock_execute.return_value = ("Claude output", "new-session-123")
        mock_remove_ansi.return_value = "Clean output"
        mock_split.return_value = ["Clean output"]

        message = AsyncMock()
        message.from_user.id = 12345
        message.text = "test prompt"

        await handle_message(message)

        # Verify session management
        mock_get.assert_called_once_with(12345)
        mock_execute.assert_called_once_with("test prompt", None)
        mock_save.assert_called_once_with(12345, "new-session-123")

        # Verify thinking message sent
        assert message.answer.call_count == 2
        first_call = message.answer.call_args_list[0]
        assert "Claude myśli" in first_call[0][0]

        # Verify result sent
        second_call = message.answer.call_args_list[1]
        assert second_call[0][0] == "Clean output"


@pytest.mark.asyncio
@patch('src.bot.get_session')
@patch('src.bot.save_session')
@patch('src.bot.execute_claude')
@patch('src.bot.remove_ansi_codes')
@patch('src.bot.split_long_message')
async def test_handle_message_success_with_session(mock_split, mock_remove_ansi, mock_execute, mock_save, mock_get):
    with patch('src.bot.ALLOWED_USER_ID', 12345):
        mock_get.return_value = "existing-session-456"
        mock_execute.return_value = ("Continued output", "existing-session-456")
        mock_remove_ansi.return_value = "Clean continued output"
        mock_split.return_value = ["Clean continued output"]

        message = AsyncMock()
        message.from_user.id = 12345
        message.text = "follow up prompt"

        await handle_message(message)

        # Verify session continuity
        mock_get.assert_called_once_with(12345)
        mock_execute.assert_called_once_with("follow up prompt", "existing-session-456")
        mock_save.assert_called_once_with(12345, "existing-session-456")

        # Verify result sent
        assert message.answer.call_count == 2


@pytest.mark.asyncio
@patch('src.bot.clear_session')
async def test_handle_new_command_authorized(mock_clear):
    with patch('src.bot.ALLOWED_USER_ID', 12345):
        message = AsyncMock()
        message.from_user.id = 12345

        await handle_new_command(message)

        mock_clear.assert_called_once_with(12345)
        message.answer.assert_called_once()
        assert "nową konwersację" in message.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_handle_new_command_unauthorized():
    with patch('src.bot.ALLOWED_USER_ID', 12345):
        message = AsyncMock()
        message.from_user.id = 99999

        await handle_new_command(message)

        message.answer.assert_called_once_with("Unauthorized")
