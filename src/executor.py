# ABOUTME: Claude Code execution wrapper for running AI prompts via subprocess
# ABOUTME: Handles subprocess calls to native Claude binary with error handling

import subprocess
import logging

logger = logging.getLogger(__name__)


def execute_claude(prompt: str) -> tuple[str, str]:
    """
    Execute Claude Code with given prompt.

    Args:
        prompt: User prompt to send to Claude

    Returns:
        Tuple of (stdout, stderr)

    Raises:
        FileNotFoundError: If claude binary not found
    """
    logger.info(f"Executing Claude with prompt: {prompt[:50]}...")

    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=None
    )

    logger.info(f"Claude returned {len(result.stdout)} chars")
    if result.stderr:
        logger.warning(f"Claude stderr: {result.stderr}")

    return result.stdout, result.stderr
