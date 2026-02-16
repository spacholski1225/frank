import pytest
from src.session import get_session, save_session, clear_session, _sessions


@pytest.fixture(autouse=True)
def clear_sessions():
    """Clear session storage before each test."""
    _sessions.clear()
    yield
    _sessions.clear()


def test_get_session_not_exists():
    result = get_session(12345)
    assert result is None


def test_save_and_get_session():
    user_id = 12345
    session_id = "abc-123-def"

    save_session(user_id, session_id)
    result = get_session(user_id)

    assert result == session_id


def test_save_session_overwrites():
    user_id = 12345

    save_session(user_id, "old-session")
    save_session(user_id, "new-session")

    result = get_session(user_id)
    assert result == "new-session"


def test_clear_session_exists():
    user_id = 12345
    save_session(user_id, "session-to-clear")

    clear_session(user_id)

    result = get_session(user_id)
    assert result is None


def test_clear_session_not_exists():
    # Should not raise error
    clear_session(99999)
    assert get_session(99999) is None


def test_multiple_users():
    save_session(111, "session-111")
    save_session(222, "session-222")
    save_session(333, "session-333")

    assert get_session(111) == "session-111"
    assert get_session(222) == "session-222"
    assert get_session(333) == "session-333"

    clear_session(222)

    assert get_session(111) == "session-111"
    assert get_session(222) is None
    assert get_session(333) == "session-333"
