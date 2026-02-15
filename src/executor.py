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
        ["claude", "-p", prompt, "--yes"],
        capture_output=True,
        text=True,
        timeout=None
    )

    return result.stdout, result.stderr
