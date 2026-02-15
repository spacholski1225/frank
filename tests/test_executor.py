import pytest
from unittest.mock import patch, MagicMock
from src.executor import execute_claude


@patch('src.executor.subprocess.run')
def test_execute_claude_success(mock_run):
    mock_run.return_value = MagicMock(
        stdout="Claude response",
        stderr="",
        returncode=0
    )

    stdout, stderr = execute_claude("test prompt")

    assert stdout == "Claude response"
    assert stderr == ""
    mock_run.assert_called_once_with(
        ["claude", "-p", "test prompt"],
        capture_output=True,
        text=True,
        timeout=None
    )


@patch('src.executor.subprocess.run')
def test_execute_claude_with_stderr(mock_run):
    mock_run.return_value = MagicMock(
        stdout="Output",
        stderr="Warning message",
        returncode=0
    )

    stdout, stderr = execute_claude("prompt")

    assert stdout == "Output"
    assert stderr == "Warning message"


@patch('src.executor.subprocess.run')
def test_execute_claude_command_not_found(mock_run):
    mock_run.side_effect = FileNotFoundError("claude: command not found")

    with pytest.raises(FileNotFoundError):
        execute_claude("prompt")
