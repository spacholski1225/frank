"""Frank the Assistant - FastAPI Server."""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from pathlib import Path
from datetime import datetime
import re

from .models.schemas import ChatRequest, ChatResponse, NutritionStatus
from .agent import FrankAgent
from .tools.food_tool import FoodTool
from .utils.markdown_parser import FoodDatabaseParser


# Global variables for components
frank_agent: FrankAgent | None = None
food_parser: FoodDatabaseParser | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize components on startup."""
    global frank_agent, food_parser

    # Get configuration from environment
    data_dir = os.getenv("FRANK_DATA_DIR", "./frank_system")
    data_path = Path(data_dir)

    # Initialize food database parser
    food_db_path = data_path / "configs" / "food_database.md"
    food_parser = FoodDatabaseParser(str(food_db_path))
    food_parser.load()

    # Initialize food tool
    vault_path = data_path / "obsidian_vault"
    food_tool = FoodTool(food_parser, str(vault_path))

    # Initialize Frank agent
    system_prompt_path = data_path / "configs" / "system_prompt.md"
    frank_agent = FrankAgent(
        food_tool=food_tool,
        system_prompt_path=str(system_prompt_path)
    )

    yield

    # Cleanup (if needed)
    frank_agent = None
    food_parser = None


# Create FastAPI app
app = FastAPI(
    title="Frank the Assistant",
    description="Local AI assistant for food tracking, notes, and calendar",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Frank the Assistant",
        "version": "0.1.0"
    }


@app.post("/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main conversational endpoint.

    Args:
        request: ChatRequest with message and optional session_id

    Returns:
        ChatResponse with Frank's response and session_id
    """
    if frank_agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Frank agent not initialized"
        )

    full_response = ""
    final_session_id = request.session_id

    try:
        async for chunk in frank_agent.chat(request.message, request.session_id):
            if chunk.get("type") == "text":
                content = chunk.get("content", "")
                if content:
                    full_response += content

            # Update session ID
            if chunk.get("session_id"):
                final_session_id = chunk["session_id"]

        return ChatResponse(
            response=full_response.strip() or "I processed your request.",
            session_id=final_session_id or "no-session"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {str(e)}"
        )


@app.post("/v1/system/refresh-db")
async def refresh_database():
    """Reload food database from markdown file.

    Returns:
        Status message with item count
    """
    if food_parser is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Food parser not initialized"
        )

    try:
        db = food_parser.load()
        return {
            "status": "reloaded",
            "item_count": len(db)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reloading database: {str(e)}"
        )


@app.get("/v1/status/nutrition", response_model=NutritionStatus)
async def nutrition_status():
    """Get today's nutrition summary from daily log.

    Returns:
        NutritionStatus with calorie and macro totals
    """
    data_dir = os.getenv("FRANK_DATA_DIR", "./frank_system")
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = Path(data_dir) / "obsidian_vault" / "Daily_Logs" / f"{today}.md"

    if not log_path.exists():
        return NutritionStatus(
            date=today,
            total_kcal=0,
            total_protein=0.0,
            total_carbs=0.0,
            total_fat=0.0,
            meal_count=0
        )

    # Parse markdown table
    content = log_path.read_text()

    total_kcal = 0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0
    meal_count = 0

    # Find table rows (skip header and separator)
    for line in content.split('\n'):
        if '|' in line and not line.strip().startswith('#'):
            parts = [p.strip() for p in line.split('|')]
            parts = [p for p in parts if p]

            # Skip header/separator
            if len(parts) == 7 and parts[0] != 'Godzina' and not parts[0].startswith('-'):
                try:
                    kcal = int(parts[2])
                    protein = float(parts[3])
                    carbs = float(parts[4])
                    fat = float(parts[5])

                    total_kcal += kcal
                    total_protein += protein
                    total_carbs += carbs
                    total_fat += fat
                    meal_count += 1
                except (ValueError, IndexError):
                    continue

    return NutritionStatus(
        date=today,
        total_kcal=total_kcal,
        total_protein=total_protein,
        total_carbs=total_carbs,
        total_fat=total_fat,
        meal_count=meal_count
    )
