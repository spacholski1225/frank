"""Pydantic models for Frank API."""
from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Frank's response")
    session_id: str = Field(..., description="Session ID for this conversation")


class NutritionStatus(BaseModel):
    """Today's nutrition summary."""
    date: str
    total_kcal: int
    total_protein: float
    total_carbs: float
    total_fat: float
    meal_count: int
