# ABOUTME: Tests for blog per-URL Claude runner
# ABOUTME: Verifies subprocess calls, output parsing, file saving

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.blog.runner import BlogRunner


def test_run_blog_returns_no_new_content_when_claude_says_so(tmp_path):
    runner = BlogRunner()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="NO_NEW_CONTENT",
            stderr=""
        )
        result = runner.fetch_blog(
            url="https://example.com/blog",
            name="Example Blog",
            output_dir=tmp_path
        )
    assert result is None
    assert list(tmp_path.iterdir()) == []


def test_run_blog_saves_file_when_content_found(tmp_path):
    runner = BlogRunner()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="---\nsource: Example Blog\nurl: https://example.com/blog\n---\n\nSome content",
            stderr=""
        )
        result = runner.fetch_blog(
            url="https://example.com/blog",
            name="Example Blog",
            output_dir=tmp_path
        )
    assert result is not None
    assert result.exists()
    assert "example.com" in result.name


def test_run_blog_raises_on_claude_failure(tmp_path):
    runner = BlogRunner()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="some error"
        )
        with pytest.raises(Exception, match="Claude execution failed"):
            runner.fetch_blog(
                url="https://example.com/blog",
                name="Example Blog",
                output_dir=tmp_path
            )
