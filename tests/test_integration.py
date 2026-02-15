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

    stdout, stderr = execute_claude(prompt)

    # Verify we got output
    assert stdout or stderr

    # Clean output
    clean = remove_ansi_codes(stdout if stdout else stderr)

    # Verify output is non-empty
    assert len(clean.strip()) > 0
