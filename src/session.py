# ABOUTME: Session storage for Claude conversation continuity per Telegram user
# ABOUTME: Manages session IDs in memory for conversation history tracking

import logging

logger = logging.getLogger(__name__)

# Global dictionary: {telegram_user_id: claude_session_id}
_sessions: dict[int, str] = {}


def get_session(user_id: int) -> str | None:
    """
    Get session ID for a user.

    Args:
        user_id: Telegram user ID

    Returns:
        Session ID if exists, None otherwise
    """
    session_id = _sessions.get(user_id)
    if session_id:
        logger.info(f"Found existing session for user {user_id}: {session_id[:8]}...")
    else:
        logger.info(f"No existing session for user {user_id}")
    return session_id


def save_session(user_id: int, session_id: str) -> None:
    """
    Save session ID for a user.

    Args:
        user_id: Telegram user ID
        session_id: Claude session ID to save
    """
    _sessions[user_id] = session_id
    logger.info(f"Saved session for user {user_id}: {session_id[:8]}...")


def clear_session(user_id: int) -> None:
    """
    Clear session ID for a user (starts fresh conversation).

    Args:
        user_id: Telegram user ID
    """
    if user_id in _sessions:
        old_session = _sessions[user_id]
        del _sessions[user_id]
        logger.info(f"Cleared session for user {user_id}: {old_session[:8]}...")
    else:
        logger.info(f"No session to clear for user {user_id}")
