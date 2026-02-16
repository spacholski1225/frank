import pytest
from src.executor import execute_claude
from src.formatter import remove_ansi_codes


@pytest.mark.integration
def test_real_claude_execution():
    """
    Integration test - requires Claude Code installed and logged in.
    Run with: pytest tests/test_integration.py -v -m integration
    """
    prompt = "Say 'hello' and nothing else"

    result_text, session_id = execute_claude(prompt)

    # Verify we got output
    assert result_text

    # Verify session ID returned
    assert session_id

    # Clean output
    clean = remove_ansi_codes(result_text)

    # Verify output is non-empty
    assert len(clean.strip()) > 0
