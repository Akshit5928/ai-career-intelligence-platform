from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.matching import calculate_match

router = APIRouter(prefix="/api/v1", tags=["career"])


class MatchRequest(BaseModel):
    user_skills: list[str] = Field(default_factory=list)
    target_roles: list[str] = Field(default_factory=list)
    target_locations: list[str] = Field(default_factory=list)
    relocation_ok: bool = True
    role_category: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    location: str | None = None
    eligibility: str | None = None
    deadline: datetime | None = None


@router.post("/match")
def match_opportunity(request: MatchRequest) -> dict:
    result = calculate_match(**request.model_dump())
    return {
        "score": result.score,
        "components": {
            "skill_score": result.skill_score,
            "role_score": result.role_score,
            "location_score": result.location_score,
            "eligibility_score": result.eligibility_score,
            "deadline_score": result.deadline_score,
        },
        "missing_skills": result.missing_skills,
        "reasons": result.reasons,
    }
