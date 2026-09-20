"""Opt-in tests using real Codex; no IMAP or Telegram calls."""
from datetime import date
import pytest
from src.executor import execute_codex
from src.newsletter.codex_runner import CodexRunner
from src.blog.summarizer import BlogSummarizer


@pytest.mark.integration
def test_real_codex_execution_and_resume():
    answer, session = execute_codex("Remember this synthetic test label: FRANK42. Reply only OK.")
    assert answer and session
    answer, resumed = execute_codex("What was the synthetic test label? Reply only with the label.", session)
    assert "FRANK42" in answer
    assert resumed == session


@pytest.mark.integration
@pytest.mark.parametrize("kind", ["newsletter", "blog"])
def test_real_saved_digest(tmp_path, kind):
    (tmp_path / "source.md").write_text(
        f"Date: {date.today()}\nSubject: Synthetic test newsletter\n"
        "This is fictional test data. Local AI library FrankTest added offline "
        "document search and quantization. Source: https://example.com/frank-test\n"
    )
    (tmp_path / "summary.md").write_text("STALE_REPORT_MUST_NOT_BE_USED")
    if kind == "newsletter":
        answer = CodexRunner().analyze_newsletters(str(tmp_path))
    else:
        answer = BlogSummarizer().summarize(tmp_path)
    assert len(answer) > 40
    assert "STALE_REPORT_MUST_NOT_BE_USED" not in answer
    assert (tmp_path / "summary.md").read_text() == answer
