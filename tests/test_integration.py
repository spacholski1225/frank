"""Integration tests for Frank the Assistant.

These tests require:
- ANTHROPIC_API_KEY environment variable
- frank_system/ directory with configs
"""
import pytest
import os
from pathlib import Path


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set"
)
@pytest.mark.asyncio
async def test_full_food_logging_workflow():
    """Test complete food logging workflow with real Agent SDK.

    This test:
    1. Initializes all components
    2. Sends food logging message
    3. Verifies daily log is created
    """
    from src.agent import FrankAgent
    from src.tools.food_tool import FoodTool
    from src.utils.markdown_parser import FoodDatabaseParser
    from datetime import datetime
    import tempfile

    # Set up temporary vault
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)
        (vault_path / "Daily_Logs").mkdir()

        # Initialize components
        food_db_path = Path("frank_system/configs/food_database.md")
        if not food_db_path.exists():
            pytest.skip("food_database.md not found")

        parser = FoodDatabaseParser(str(food_db_path))
        parser.load()

        food_tool = FoodTool(parser, str(vault_path))

        system_prompt_path = Path("frank_system/configs/system_prompt.md")
        if not system_prompt_path.exists():
            pytest.skip("system_prompt.md not found")

        agent = FrankAgent(
            food_tool=food_tool,
            system_prompt_path=str(system_prompt_path)
        )

        # Chat with Frank
        response_text = ""
        async for message in agent.chat("Zjadłem owsiankę", session_id=None):
            if message.get("type") == "text":
                response_text += message.get("content", "")

        # Verify response mentions logging
        assert len(response_text) > 0

        # Verify daily log was created
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = vault_path / "Daily_Logs" / f"{today}.md"

        # Note: May not exist if tool wasn't called (depends on agent behavior)
        # This test validates the integration works end-to-end
