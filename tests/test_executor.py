import pytest
import json
from unittest.mock import patch, MagicMock
from src.executor import execute_claude


@patch('src.executor.subprocess.run')
def test_execute_claude_success_no_session(mock_run):
    json_response = {
        "result": "Claude response text",
        "session_id": "new-session-123"
    }
    mock_run.return_value = MagicMock(
        stdout=json.dumps(json_response),
        stderr="",
        returncode=0
    )

    result_text, session_id = execute_claude("test prompt")

    assert result_text == "Claude response text"
    assert session_id == "new-session-123"
    mock_run.assert_called_once_with(
        ["claude", "-p", "test prompt", "--output-format", "json"],
        capture_output=True,
        text=True,
        timeout=None
    )


@patch('src.executor.subprocess.run')
def test_execute_claude_success_with_session(mock_run):
    json_response = {
        "result": "Continued response",
        "session_id": "existing-session-456"
    }
    mock_run.return_value = MagicMock(
        stdout=json.dumps(json_response),
        stderr="",
        returncode=0
    )

    result_text, session_id = execute_claude("test prompt", session_id="existing-session-456")

    assert result_text == "Continued response"
    assert session_id == "existing-session-456"
    mock_run.assert_called_once_with(
        ["claude", "-p", "test prompt", "--output-format", "json", "--resume", "existing-session-456"],
        capture_output=True,
        text=True,
        timeout=None
    )


@patch('src.executor.subprocess.run')
def test_execute_claude_with_stderr(mock_run):
    json_response = {
        "result": "Output with warning",
        "session_id": "session-789"
    }
    mock_run.return_value = MagicMock(
        stdout=json.dumps(json_response),
        stderr="Warning message",
        returncode=0
    )

    result_text, session_id = execute_claude("prompt")

    assert result_text == "Output with warning"
    assert session_id == "session-789"


@patch('src.executor.subprocess.run')
def test_execute_claude_invalid_json(mock_run):
    mock_run.return_value = MagicMock(
        stdout="Not valid JSON",
        stderr="",
        returncode=0
    )

    with pytest.raises(ValueError, match="Invalid JSON from Claude"):
        execute_claude("prompt")


@patch('src.executor.subprocess.run')
def test_execute_claude_missing_result(mock_run):
    json_response = {
        "session_id": "session-only"
    }
    mock_run.return_value = MagicMock(
        stdout=json.dumps(json_response),
        stderr="",
        returncode=0
    )

    result_text, session_id = execute_claude("prompt")

    assert result_text == ""
    assert session_id == "session-only"


@patch('src.executor.subprocess.run')
def test_execute_claude_missing_session_id(mock_run):
    json_response = {
        "result": "Response without session"
    }
    mock_run.return_value = MagicMock(
        stdout=json.dumps(json_response),
        stderr="",
        returncode=0
    )

    result_text, session_id = execute_claude("prompt")

    assert result_text == "Response without session"
    assert session_id == ""


@patch('src.executor.subprocess.run')
def test_execute_claude_command_not_found(mock_run):
    mock_run.side_effect = FileNotFoundError("claude: command not found")

    with pytest.raises(FileNotFoundError):
        execute_claude("prompt")
