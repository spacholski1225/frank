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
