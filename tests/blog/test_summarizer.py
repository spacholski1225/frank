from unittest.mock import patch
import pytest
from src.blog.summarizer import BlogSummarizer


def test_summarize_overwrites_stale_report(tmp_path):
    (tmp_path / "blog.md").write_text("some content")
    (tmp_path / "summary.md").write_text("stale report")
    with patch("src.blog.summarizer.execute_codex", return_value=("Nowe wnioski", "123")):
        assert BlogSummarizer().summarize(tmp_path) == "Nowe wnioski"
    assert (tmp_path / "summary.md").read_text() == "Nowe wnioski"


def test_summarize_raises_on_empty_folder(tmp_path):
    with pytest.raises(ValueError, match="No blog summaries"):
        BlogSummarizer().summarize(tmp_path)
