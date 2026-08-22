from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator


class ScoringCriteriaSchema(BaseModel):
    ideaUsp: float = Field(..., ge=0.0, le=5.0, description="Startup Idea and USP (0-5)")
    targetMarket: float = Field(..., ge=0.0, le=5.0, description="Target Market and Size (0-5)")
    growthPotential: float = Field(..., ge=0.0, le=5.0, description="Growth Potential (0-5)")
    revenueModel: float = Field(..., ge=0.0, le=5.0, description="Revenue Model (0-5)")
    stageFuturePlans: float = Field(..., ge=0.0, le=5.0, description="Stage of Startup and Future Plans (0-5)")
    teamMembers: float = Field(..., ge=0.0, le=5.0, description="Team Members (0-5)")


class MentorSubmitScoreSchema(BaseModel):
    teamId: str = Field(..., min_length=1)
    scores: ScoringCriteriaSchema
    feedback: Optional[str] = Field("", max_length=1000)


class AdminUpdateScoreSchema(BaseModel):
    teamId: str = Field(..., min_length=1)
    mentorId: str = Field(..., min_length=1)
    scores: ScoringCriteriaSchema
    feedback: Optional[str] = Field("", max_length=1000)
