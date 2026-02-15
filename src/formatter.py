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
