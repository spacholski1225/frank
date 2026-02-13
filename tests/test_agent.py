import pytest
import tempfile
from pathlib import Path
from src.agent import FrankAgent
from src.tools.food_tool import FoodTool
from src.utils.markdown_parser import FoodDatabaseParser


@pytest.fixture
def temp_system_prompt():
    """Create temporary system prompt file"""
    import os
    content = "# Frank\n\nYou are Frank, a helpful assistant."
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        temp_path = f.name
    yield temp_path
    # Cleanup after test
    os.unlink(temp_path)


def test_frank_agent_initialization(temp_system_prompt):
    """Test FrankAgent loads system prompt"""
    from unittest.mock import Mock

    mock_food_tool = Mock(spec=FoodTool)

    agent = FrankAgent(
        food_tool=mock_food_tool,
        system_prompt_path=temp_system_prompt
    )

    assert agent.food_tool == mock_food_tool
    assert "Frank" in agent.system_prompt
    assert len(agent.sessions) == 0


@pytest.mark.asyncio
async def test_frank_agent_chat_yields_messages(temp_system_prompt, monkeypatch):
    """Test that chat method yields messages from Agent SDK"""
    from unittest.mock import Mock, AsyncMock
    import asyncio

    mock_food_tool = Mock(spec=FoodTool)
    agent = FrankAgent(
        food_tool=mock_food_tool,
        system_prompt_path=temp_system_prompt
    )

    # Mock the query function from Agent SDK
    async def mock_query(*args, **kwargs):
        # Simulate SDK message stream
        class MockInitMessage:
            type = "system"
            subtype = "init"
            session_id = "test-session-123"

        class MockTextMessage:
            type = "text"
            result = "Hello, I'm Frank!"

        yield MockInitMessage()
        yield MockTextMessage()

    monkeypatch.setattr("src.agent.query", mock_query)

    messages = []
    async for msg in agent.chat("Hello", session_id=None):
        messages.append(msg)

    assert len(messages) == 2
    assert messages[0]["type"] == "system"
    assert messages[1]["type"] == "text"
    assert messages[1]["content"] == "Hello, I'm Frank!"
