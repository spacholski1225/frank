import tempfile
import os
from src.utils.markdown_parser import FoodItem, FoodDatabaseParser

def test_food_item_creation():
    """Test FoodItem dataclass creation"""
    item = FoodItem(
        name="Owsianka",
        kcal=450,
        protein=20.0,
        carbs=60.0,
        fat=15.0,
        unit="porcja"
    )
    assert item.name == "Owsianka"
    assert item.kcal == 450
    assert item.protein == 20.0


def test_parse_food_database():
    """Test parsing markdown table from food_database.md"""
    # Create temporary markdown file
    markdown_content = """# Moja Baza Posiłków

| Nazwa (Alias) | Kcal | Białko (g) | Węgle (g) | Tłuszcz (g) | Jednostka |
|---------------|------|------------|-----------|-------------|-----------|
| Owsianka      | 450  | 20         | 60        | 15          | porcja    |
| Banan         | 105  | 1          | 27        | 0           | sztuka    |
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(markdown_content)
        temp_path = f.name

    try:
        parser = FoodDatabaseParser(temp_path)
        db = parser.load()

        assert "owsianka" in db
        assert db["owsianka"].kcal == 450
        assert db["owsianka"].protein == 20.0

        assert "banan" in db
        assert db["banan"].kcal == 105
    finally:
        os.unlink(temp_path)


def test_case_insensitive_lookup():
    """Test that lookup works regardless of case"""
    markdown_content = """# Moja Baza Posiłków

| Nazwa (Alias) | Kcal | Białko (g) | Węgle (g) | Tłuszcz (g) | Jednostka |
|---------------|------|------------|-----------|-------------|-----------|
| Owsianka      | 450  | 20         | 60        | 15          | porcja    |
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(markdown_content)
        temp_path = f.name

    try:
        parser = FoodDatabaseParser(temp_path)
        parser.load()

        # All these should find the item
        assert parser.lookup("Owsianka") is not None
        assert parser.lookup("owsianka") is not None
        assert parser.lookup("OWSIANKA") is not None
        assert parser.lookup("oWsIaNkA") is not None

        # This should not find anything
        assert parser.lookup("Pizza") is None
    finally:
        os.unlink(temp_path)
