"""Food tracking tool for Frank the Assistant."""
from typing import Optional
from datetime import datetime
import os
from pathlib import Path


class FoodTool:
    """Tool for looking up food, estimating nutrition, and logging to daily journal."""

    def __init__(self, food_db_parser, vault_path: str):
        """Initialize FoodTool.

        Args:
            food_db_parser: FoodDatabaseParser instance
            vault_path: Path to Obsidian vault directory
        """
        self.food_db = food_db_parser
        self.vault_path = Path(vault_path)

    async def lookup_and_log(
        self,
        food_items: list[str],
        meal_type: str = "snack"
    ) -> dict:
        """Look up food items and prepare for logging.

        For items in database: return full nutrition data
        For items not in database: return needs_estimation flag

        Args:
            food_items: List of food names
            meal_type: Type of meal

        Returns:
            Dict with items list and meal_type
        """
        results = []

        for item_name in food_items:
            food = self.food_db.lookup(item_name)

            if food:
                # Found in database
                results.append({
                    "name": item_name,
                    "nutrition": {
                        "kcal": food.kcal,
                        "protein": food.protein,
                        "carbs": food.carbs,
                        "fat": food.fat
                    },
                    "source": "Database"
                })
            else:
                # Not found - agent will estimate
                results.append({
                    "name": item_name,
                    "nutrition": None,
                    "source": "needs_estimation"
                })

        return {
            "items": results,
            "meal_type": meal_type
        }

    def log_to_daily(self, items: list[dict], meal_type: str = "snack"):
        """Append food items to today's daily log.

        Args:
            items: List of food items with nutrition data
            meal_type: Type of meal (breakfast, lunch, dinner, snack)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        log_dir = self.vault_path / "Daily_Logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{today}.md"

        # Create file if it doesn't exist
        if not log_file.exists():
            log_file.write_text(f"# Daily Log - {today}\n\n")

        # Append items
        current_time = datetime.now().strftime("%H:%M")

        with open(log_file, 'a', encoding='utf-8') as f:
            # Check if nutrition table exists
            content = log_file.read_text()
            if "## Dziennik Żywieniowy" not in content:
                f.write("## Dziennik Żywieniowy\n\n")
                f.write("| Godzina | Posiłek | Kcal | B | W | T | Źródło |\n")
                f.write("|---------|---------|------|---|---|---|--------|\n")

            # Add each item
            for item in items:
                name = item["name"]
                nutrition = item["nutrition"]
                source = item["source"]

                row = (
                    f"| {current_time} | {name} | {nutrition['kcal']} | "
                    f"{nutrition['protein']:.0f} | {nutrition['carbs']:.0f} | "
                    f"{nutrition['fat']:.0f} | {source} |\n"
                )
                f.write(row)


# Tool definition for Claude Agent SDK
FOOD_TOOL_DEFINITION = {
    "name": "food_lookup_and_log",
    "description": "Look up food items in user's personal database, estimate nutrition if not found, and log to daily journal",
    "input_schema": {
        "type": "object",
        "properties": {
            "food_items": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of food items the user ate (e.g., ['owsianka', 'banan'])"
            },
            "meal_type": {
                "type": "string",
                "enum": ["breakfast", "lunch", "dinner", "snack"],
                "description": "Type of meal",
                "default": "snack"
            }
        },
        "required": ["food_items"]
    }
}
