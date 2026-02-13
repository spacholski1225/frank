import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path
from src.tools.food_tool import FoodTool
from src.utils.markdown_parser import FoodDatabaseParser, FoodItem


@pytest.fixture
def temp_vault():
    """Create temporary vault directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)
        (vault_path / "Daily_Logs").mkdir(parents=True)
        yield vault_path


@pytest.fixture
def mock_food_parser():
    """Create mock food database parser with sample data"""
    parser = FoodDatabaseParser.__new__(FoodDatabaseParser)
    parser._cache = {
        "owsianka": FoodItem("Owsianka", 450, 20.0, 60.0, 15.0, "porcja"),
        "banan": FoodItem("Banan", 105, 1.0, 27.0, 0.0, "sztuka")
    }
    return parser


@pytest.mark.asyncio
async def test_log_to_daily_creates_file(temp_vault, mock_food_parser):
    """Test that logging creates daily log file"""
    tool = FoodTool(mock_food_parser, str(temp_vault))

    items = [
        {
            "name": "Owsianka",
            "nutrition": {"kcal": 450, "protein": 20.0, "carbs": 60.0, "fat": 15.0},
            "source": "Database"
        }
    ]

    tool.log_to_daily(items, "breakfast")

    # Check file was created
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = temp_vault / "Daily_Logs" / f"{today}.md"

    assert log_file.exists()


@pytest.mark.asyncio
async def test_lookup_found_in_database(mock_food_parser):
    """Test lookup for item that exists in database"""
    tool = FoodTool(mock_food_parser, "/tmp")

    result = await tool.lookup_and_log(["owsianka"], "breakfast")

    assert len(result["items"]) == 1
    assert result["items"][0]["name"] == "owsianka"
    assert result["items"][0]["source"] == "Database"
    assert result["items"][0]["nutrition"]["kcal"] == 450


@pytest.mark.asyncio
async def test_lookup_not_found_needs_estimation(mock_food_parser):
    """Test lookup for item not in database returns needs_estimation"""
    tool = FoodTool(mock_food_parser, "/tmp")

    result = await tool.lookup_and_log(["pizza"], "lunch")

    assert len(result["items"]) == 1
    assert result["items"][0]["name"] == "pizza"
    assert result["items"][0]["source"] == "needs_estimation"
    assert result["items"][0]["nutrition"] is None


@pytest.mark.asyncio
async def test_full_lookup_and_log_workflow(temp_vault, mock_food_parser):
    """Test complete workflow: lookup + log to daily file"""
    tool = FoodTool(mock_food_parser, str(temp_vault))

    # Lookup mixed items (found + not found)
    result = await tool.lookup_and_log(["owsianka", "pizza", "banan"], "breakfast")

    # Prepare items for logging (simulate agent estimating pizza)
    items_to_log = []
    for item in result["items"]:
        if item["source"] == "Database":
            items_to_log.append(item)
        elif item["source"] == "needs_estimation":
            # Simulate LLM estimation
            item["nutrition"] = {"kcal": 250, "protein": 12.0, "carbs": 30.0, "fat": 10.0}
            item["source"] = "Estymacja"
            items_to_log.append(item)

    # Log to daily
    tool.log_to_daily(items_to_log, "breakfast")

    # Verify log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = temp_vault / "Daily_Logs" / f"{today}.md"

    assert log_file.exists()
    content = log_file.read_text()
    assert "owsianka" in content
    assert "pizza" in content
    assert "banan" in content
    assert "450" in content  # owsianka kcal
    assert "250" in content  # pizza kcal (estimated)
