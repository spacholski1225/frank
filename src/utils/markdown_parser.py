"""Markdown parser for food database and daily logs."""
from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class FoodItem:
    """Represents a food item with nutritional information."""
    name: str
    kcal: int
    protein: float
    carbs: float
    fat: float
    unit: str


class FoodDatabaseParser:
    """Parser for food_database.md markdown tables."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._cache: dict[str, FoodItem] = {}

    def load(self) -> dict[str, FoodItem]:
        """Parse food_database.md and return dict of food items.

        Returns:
            Dict mapping lowercase food names to FoodItem objects
        """
        self._cache.clear()

        with open(self.db_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find table rows (skip header and separator)
        lines = content.split('\n')
        in_table = False

        for line in lines:
            # Check if this is a table row (contains | separators)
            if '|' in line and not line.strip().startswith('#'):
                parts = [p.strip() for p in line.split('|')]
                # Filter out empty parts from leading/trailing |
                parts = [p for p in parts if p]

                # Skip header row and separator row
                if len(parts) == 6 and parts[0] != 'Nazwa (Alias)' and not parts[0].startswith('-'):
                    try:
                        name = parts[0]
                        kcal = int(parts[1])
                        protein = float(parts[2])
                        carbs = float(parts[3])
                        fat = float(parts[4])
                        unit = parts[5]

                        food_item = FoodItem(
                            name=name,
                            kcal=kcal,
                            protein=protein,
                            carbs=carbs,
                            fat=fat,
                            unit=unit
                        )

                        # Store with lowercase key for case-insensitive lookup
                        self._cache[name.lower()] = food_item
                    except (ValueError, IndexError):
                        # Skip malformed rows
                        continue

        return self._cache

    def lookup(self, food_name: str) -> Optional[FoodItem]:
        """Look up food item by name (case-insensitive).

        Args:
            food_name: Name of food to look up

        Returns:
            FoodItem if found, None otherwise
        """
        return self._cache.get(food_name.lower())
