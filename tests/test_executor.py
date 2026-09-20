import json
import subprocess
from pathlib import Path
from unittest.mock import patch
import pytest
from src.executor import execute_codex


def cli_result(cmd, **kwargs):
    Path(cmd[cmd.index("--output-last-message") + 1]).write_text("Final report", encoding="utf-8")
    return subprocess.CompletedProcess(cmd, 0, json.dumps({"type": "thread.started", "thread_id": "thread-123"}) + "\n" + json.dumps({"type": "turn.completed"}), "progress")


def test_final_answer_and_session_not_progress():
    with patch("src.executor.subprocess.run", side_effect=cli_result) as run:
        assert execute_codex("private prompt") == ("Final report", "thread-123")
    cmd = run.call_args.args[0]
    assert "private prompt" not in cmd
    assert run.call_args.kwargs["input"] == "private prompt"
    assert 'web_search="disabled"' in cmd
    assert "read-only" in cmd


def test_resume_and_web_search(monkeypatch):
    monkeypatch.setenv("CODEX_BIN", "/custom/codex")
    monkeypatch.setenv("CODEX_MODEL", "test-model")
    with patch("src.executor.subprocess.run", side_effect=cli_result) as run:
        execute_codex("continue", "thread-123", web_search=True)
    cmd = run.call_args.args[0]
    assert cmd[0] == "/custom/codex"
    assert cmd[cmd.index("resume") + 1] == "thread-123"
    assert 'web_search="live"' in cmd
    assert "test-model" in cmd


@pytest.mark.parametrize("events,returncode,expected", [
    ('not json', 0, "Invalid JSON"),
    ('{"type":"turn.failed","error":{"message":"limit"}}', 0, "execution failed"),
    ('', 1, "execution failed"),
    ('{"type":"thread.started","thread_id":"123"}', 0, "no final answer"),
])
def test_failures_never_become_reports(events, returncode, expected):
    with patch("src.executor.subprocess.run", return_value=subprocess.CompletedProcess([], returncode, events, "error")):
        with pytest.raises((RuntimeError, ValueError), match=expected):
            execute_codex("prompt")


def test_missing_binary():
    with patch("src.executor.subprocess.run", side_effect=FileNotFoundError):
        with pytest.raises(RuntimeError, match="CLI not found"):
            execute_codex("prompt")


def test_timeout():
    with patch("src.executor.subprocess.run", side_effect=subprocess.TimeoutExpired("codex", 1)):
        with pytest.raises(TimeoutError, match="timeout"):
            execute_codex("prompt", timeout=1)
