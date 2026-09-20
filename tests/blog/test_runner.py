from datetime import date
from unittest.mock import patch
import pytest
from src.blog.runner import BlogRunner


@pytest.mark.parametrize("answer", ["NO_NEW_CONTENT", "FETCH_ERROR", "# Polski raport"])
def test_blog_fetch_results(tmp_path, answer):
    with patch("src.blog.runner.execute_codex", return_value=(answer, "123")) as run:
        if answer == "FETCH_ERROR":
            with pytest.raises(RuntimeError, match="Cannot fetch"):
                BlogRunner().fetch_blog("https://example.com", "Example", tmp_path)
        else:
            result = BlogRunner().fetch_blog("https://example.com", "Example", tmp_path)
            if answer == "NO_NEW_CONTENT":
                assert result is None
                assert not list(tmp_path.iterdir())
            else:
                assert result.read_text() == answer
    assert run.call_args.kwargs["web_search"] is True
    assert date.today().isoformat() in run.call_args.args[0]


def test_marker_inside_article_is_not_no_content(tmp_path):
    with patch("src.blog.runner.execute_codex", return_value=("Article about NO_NEW_CONTENT markers", "123")):
        assert BlogRunner().fetch_blog("https://example.com", "Example", tmp_path)
