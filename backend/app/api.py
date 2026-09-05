from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.db import get_supabase
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


@router.post("/match/refresh")
def refresh_all_matches() -> dict:
    """Recalculate and persist matches for every active internship."""
    db = get_supabase()

    config_response = db.table("agent_config").select(
        "target_roles,target_locations,relocation_ok"
    ).order("created_at", desc=True).limit(1).execute()
    config_rows = config_response.data or []
    if not config_rows:
        raise HTTPException(status_code=404, detail="Agent configuration not found")
    config = config_rows[0]

    skills_response = db.table("user_skills").select("skill_name").eq("status", "active").execute()
    user_skills = [row["skill_name"] for row in (skills_response.data or [])]

    internships_response = db.table("internships").select(
        "id,role_category,required_skills,preferred_skills,location,eligibility,deadline,status"
    ).eq("status", "active").execute()
    internships = internships_response.data or []

    now = datetime.now(timezone.utc)
    match_rows = []
    updates = []
    for internship in internships:
        result = calculate_match(
            user_skills=user_skills,
            target_roles=config.get("target_roles") or [],
            target_locations=config.get("target_locations") or [],
            relocation_ok=bool(config.get("relocation_ok")),
            role_category=internship.get("role_category") or "",
            required_skills=internship.get("required_skills") or [],
            preferred_skills=internship.get("preferred_skills") or [],
            location=internship.get("location"),
            eligibility=internship.get("eligibility"),
            deadline=internship.get("deadline"),
            now=now,
        )
        match_rows.append({
            "internship_id": internship["id"],
            "score": result.score,
            "skill_score": result.skill_score,
            "role_score": result.role_score,
            "location_score": result.location_score,
            "eligibility_score": result.eligibility_score,
            "deadline_score": result.deadline_score,
            "missing_skills": result.missing_skills,
            "reasons": result.reasons,
            "calculated_at": now.isoformat(),
        })
        priority = "high" if result.score >= 75 else "medium" if result.score >= 50 else "low"
        updates.append({
            "id": internship["id"],
            "match_score": result.score,
            "missing_skills": result.missing_skills,
            "priority": priority,
        })

    if match_rows:
        db.table("internship_matches").upsert(match_rows, on_conflict="internship_id").execute()
        for update in updates:
            internship_id = update.pop("id")
            db.table("internships").update(update).eq("id", internship_id).execute()

    return {"processed": len(match_rows), "calculated_at": now.isoformat()}


@router.get("/matches")
def get_matches(limit: int = 20) -> list[dict]:
    """Return persisted matches joined with the core internship fields."""
    db = get_supabase()
    response = db.table("internship_matches").select(
        "id,internship_id,score,skill_score,role_score,location_score,"
        "eligibility_score,deadline_score,missing_skills,reasons,calculated_at,"
        "internships(company_name,role_title,role_category,location,work_mode,stipend,deadline,application_url)"
    ).order("score", desc=True).limit(min(max(limit, 1), 100)).execute()
    return response.data or []
