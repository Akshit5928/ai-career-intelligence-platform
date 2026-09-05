from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re


ROLE_ALIASES = {
    "ai/ml intern": {"ai/ml", "ai engineer", "machine learning", "genai", "llm/rag"},
    "data analyst intern": {"data analyst", "data analysis"},
    "data science intern": {"data science", "machine learning", "ai/ml"},
    "ai engineer intern": {"ai engineer", "ai/ml", "genai", "llm/rag"},
    "genai/llm/rag intern": {"genai", "llm/rag", "ai engineer"},
    "software engineering intern": {"software engineering", "backend", "python/backend"},
}

SKILL_ALIASES = {
    "github": "git/github",
    "git": "git/github",
    "git/github": "git/github",
    "llms": "llm",
    "large language models": "llm",
    "generative ai": "generative ai",
    "gen ai": "generative ai",
    "machine-learning": "machine learning",
    "powerbi": "power bi",
}


@dataclass(frozen=True)
class MatchResult:
    score: float
    skill_score: float
    role_score: float
    location_score: float
    eligibility_score: float
    deadline_score: float
    missing_skills: list[str]
    reasons: list[str]


def _norm(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"\s+", " ", value)
    return SKILL_ALIASES.get(value, value)


def _norm_skills(skills: list[str]) -> set[str]:
    return {_norm(skill) for skill in skills if skill and skill.strip()}


def _role_family(role: str) -> str:
    value = _norm(role)
    for family, aliases in ROLE_ALIASES.items():
        if value in aliases or family == value:
            return family
    return value


def _location_score(opportunity_location: str | None, target_locations: list[str]) -> float:
    if not opportunity_location:
        return 50.0
    location = _norm(opportunity_location)
    targets = {_norm(item) for item in target_locations}
    if "remote" in location and "remote" in targets:
        return 100.0
    if any(target in location or location in target for target in targets):
        return 100.0
    if "india" in location and "india" in targets:
        return 100.0
    return 0.0


def _eligibility_score(eligibility: str | None) -> float:
    if not eligibility:
        return 50.0
    text = eligibility.lower()
    positive = ("student", "students", "fresher", "freshers", "no experience", "3rd year", "b.tech")
    negative = ("experience required", "years of experience")
    if any(term in text for term in positive) and not any(term in text for term in negative):
        return 100.0
    if any(term in text for term in negative):
        return 0.0
    return 50.0


def _deadline_score(deadline: datetime | None, now: datetime | None = None) -> float:
    if deadline is None:
        return 50.0
    now = now or datetime.now(timezone.utc)
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    days = (deadline - now).total_seconds() / 86400
    if days < 0:
        return 0.0
    if days <= 3:
        return 100.0
    if days <= 7:
        return 90.0
    if days <= 14:
        return 75.0
    if days <= 30:
        return 60.0
    return 40.0


def calculate_match(
    *,
    user_skills: list[str],
    target_roles: list[str],
    target_locations: list[str],
    relocation_ok: bool,
    role_category: str,
    required_skills: list[str],
    preferred_skills: list[str] | None = None,
    location: str | None = None,
    eligibility: str | None = None,
    deadline: datetime | None = None,
    now: datetime | None = None,
) -> MatchResult:
    user = _norm_skills(user_skills)
    required = _norm_skills(required_skills)
    preferred = _norm_skills(preferred_skills or [])

    if required:
        required_hits = len(user & required) / len(required)
        preferred_hits = len(user & preferred) / len(preferred) if preferred else 1.0
        skill_score = (required_hits * 0.8 + preferred_hits * 0.2) * 100
    else:
        skill_score = 50.0

    target_families = {_role_family(role) for role in target_roles}
    opportunity_family = _role_family(role_category)
    role_score = 100.0 if opportunity_family in target_families else 25.0

    location_score = _location_score(location, target_locations)
    if location_score == 0.0 and relocation_ok:
        location_score = 60.0

    eligibility_score = _eligibility_score(eligibility)
    deadline_score = _deadline_score(deadline, now)

    score = (
        skill_score * 0.50
        + role_score * 0.20
        + location_score * 0.15
        + eligibility_score * 0.10
        + deadline_score * 0.05
    )

    missing = [skill for skill in required_skills if _norm(skill) not in user]
    reasons = []
    if skill_score >= 70:
        reasons.append("Strong skill overlap with required skills")
    elif skill_score >= 40:
        reasons.append("Partial skill overlap; learning gaps remain")
    else:
        reasons.append("Large skill gap against required skills")
    if role_score == 100:
        reasons.append("Role aligns with a target career direction")
    if location_score >= 100:
        reasons.append("Location/work mode matches target preferences")
    if deadline_score >= 90:
        reasons.append("Deadline is approaching; prioritize review")

    return MatchResult(
        score=round(score, 2),
        skill_score=round(skill_score, 2),
        role_score=round(role_score, 2),
        location_score=round(location_score, 2),
        eligibility_score=round(eligibility_score, 2),
        deadline_score=round(deadline_score, 2),
        missing_skills=missing,
        reasons=reasons,
    )
