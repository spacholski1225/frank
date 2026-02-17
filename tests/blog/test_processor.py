# ABOUTME: Tests for blog processor orchestrator
# ABOUTME: Verifies full pipeline: sources loading, per-blog fetch, summarization

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.blog.processor import BlogProcessor


@pytest.fixture
def sources_file(tmp_path):
    sources = {
        "sources": [
            {"url": "https://blog.example.com", "name": "Example Blog"},
            {"url": "https://another.dev", "name": "Another Dev"},
        ]
    }
    f = tmp_path / "blog_sources.json"
    f.write_text(json.dumps(sources))
    return f


def test_process_returns_success_with_summary(tmp_path, sources_file):
    processor = BlogProcessor(sources_file=sources_file, base_dir=tmp_path)

    with patch.object(processor.runner, "fetch_blog") as mock_fetch, \
         patch.object(processor.summarizer, "summarize") as mock_summarize:

        mock_fetch.side_effect = [
            tmp_path / "blog_example_com.md",
            None  # second blog has no new content
        ]
        mock_summarize.return_value = "## Summary\n\ngreat content"

        result = processor.process()

    assert result["success"] is True
    assert result["blog_count"] == 1
    assert "great content" in result["summary"]


def test_process_returns_no_content_when_all_blogs_empty(tmp_path, sources_file):
    processor = BlogProcessor(sources_file=sources_file, base_dir=tmp_path)

    with patch.object(processor.runner, "fetch_blog", return_value=None):
        result = processor.process()

    assert result["success"] is True
    assert result["blog_count"] == 0
    assert result["summary"] == "No new blog posts this week."


def test_process_handles_missing_sources_file(tmp_path):
    processor = BlogProcessor(
        sources_file=tmp_path / "nonexistent.json",
        base_dir=tmp_path
    )
    result = processor.process()
    assert result["success"] is False
    assert "error" in result
