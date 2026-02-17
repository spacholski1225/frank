# ABOUTME: Tests for blog folder summarizer
# ABOUTME: Verifies Claude invocation and summary file creation

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.blog.summarizer import BlogSummarizer


def test_summarize_returns_summary_text(tmp_path):
    (tmp_path / "blog_example_com.md").write_text("some content")
    summarizer = BlogSummarizer()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="## Summary\n\nKey insights here",
            stderr=""
        )
        result = summarizer.summarize(tmp_path)
    assert "Key insights" in result


def test_summarize_reads_summary_file_if_written(tmp_path):
    (tmp_path / "blog_example_com.md").write_text("some content")
    summarizer = BlogSummarizer()

    def fake_run(*args, **kwargs):
        (tmp_path / "summary.md").write_text("summary from file")
        return MagicMock(returncode=0, stdout="", stderr="")

    with patch("subprocess.run", side_effect=fake_run):
        result = summarizer.summarize(tmp_path)

    assert result == "summary from file"


def test_summarize_raises_on_empty_folder(tmp_path):
    summarizer = BlogSummarizer()
    with pytest.raises(ValueError, match="No blog summaries"):
        summarizer.summarize(tmp_path)
