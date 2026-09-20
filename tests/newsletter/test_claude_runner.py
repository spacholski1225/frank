from unittest.mock import patch
import pytest
from src.newsletter.codex_runner import CodexRunner


def test_newsletter_report_replaces_stale_summary(tmp_path):
    (tmp_path / "mail.md").write_text("Local LLM news")
    (tmp_path / "summary.md").write_text("old report")
    with patch("src.newsletter.codex_runner.execute_codex", return_value=("Nowy raport", "123")) as run:
        assert CodexRunner().analyze_newsletters(str(tmp_path)) == "Nowy raport"
    assert (tmp_path / "summary.md").read_text() == "Nowy raport"
    assert str(tmp_path) in run.call_args.args[0]
    assert "Local LLM" in run.call_args.args[0]


def test_newsletter_failure_preserves_previous_report(tmp_path):
    (tmp_path / "mail.md").write_text("news")
    (tmp_path / "summary.md").write_text("old report")
    with patch("src.newsletter.codex_runner.execute_codex", side_effect=TimeoutError("timeout")):
        with pytest.raises(TimeoutError):
            CodexRunner().analyze_newsletters(str(tmp_path))
    assert (tmp_path / "summary.md").read_text() == "old report"


def test_no_source_emails(tmp_path):
    (tmp_path / "summary.md").write_text("old report")
    with pytest.raises(ValueError, match="No newsletter"):
        CodexRunner().analyze_newsletters(str(tmp_path))
