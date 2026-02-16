# ABOUTME: Claude Code execution wrapper for running AI prompts via subprocess
# ABOUTME: Handles subprocess calls to native Claude binary with error handling

import subprocess
import logging
import json

logger = logging.getLogger(__name__)


def execute_claude(prompt: str, session_id: str | None = None) -> tuple[str, str]:
    """
    Execute Claude Code with given prompt, optionally continuing a session.

    Args:
        prompt: User prompt to send to Claude
        session_id: Optional session ID to resume conversation

    Returns:
        Tuple of (result_text, new_session_id)

    Raises:
        FileNotFoundError: If claude binary not found
        ValueError: If JSON output cannot be parsed
    """
    logger.info(f"Executing Claude with prompt: {prompt[:50]}...")

    # Build command
    cmd = ["claude", "-p", prompt, "--output-format", "json"]
    if session_id:
        logger.info(f"Resuming session: {session_id[:8]}...")
        cmd.extend(["--resume", session_id])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=None
    )

    logger.info(f"Claude returned {len(result.stdout)} chars")
    if result.stderr:
        logger.warning(f"Claude stderr: {result.stderr}")

    # Parse JSON output
    try:
        response = json.loads(result.stdout)
        result_text = response.get("result", "")
        new_session_id = response.get("session_id", "")

        if not new_session_id:
            logger.warning("No session_id in Claude response")

        logger.info(f"Parsed response: {len(result_text)} chars, session: {new_session_id[:8]}...")
        return result_text, new_session_id

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude JSON output: {e}")
        logger.error(f"Raw output: {result.stdout[:200]}...")
        raise ValueError(f"Invalid JSON from Claude: {e}")
