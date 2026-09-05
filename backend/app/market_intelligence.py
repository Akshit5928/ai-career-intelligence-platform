from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

from backend.app.matching import _norm


@dataclass(frozen=True)
class SkillDemand:
    skill_name: str
    demand_count: int
    demand_share: float
    user_proficiency: int
    target_proficiency: int
    gap_score: float
    priority: str


def _priority(gap_score: float) -> str:
    if gap_score >= 70:
        return "critical"
    if gap_score >= 45:
        return "high"
    if gap_score >= 20:
        return "medium"
    return "low"


def analyze_market(
    internships: list[dict],
    user_skills: list[dict],
    role_filter: list[str] | None = None,
    window_days: int = 90,
) -> list[SkillDemand]:
    """Aggregate skill demand and compare it with the user's verified proficiency.

    Demand is opportunity-level: a skill counts at most once per internship.
    Gap score combines market demand and the distance from target proficiency.
    """
    role_filter_norm = {_norm(role) for role in (role_filter or [])}
    relevant = []
    for internship in internships:
        if role_filter_norm:
            role = _norm(internship.get("role_category") or "")
            title = _norm(internship.get("role_title") or "")
            if not any(target in role or target in title for target in role_filter_norm):
                continue
        relevant.append(internship)

    opportunities = len(relevant)
    if opportunities == 0:
        return []

    counts: Counter[str] = Counter()
    display_names: dict[str, str] = {}
    for internship in relevant:
        seen: set[str] = set()
        for raw_skill in (internship.get("required_skills") or []) + (internship.get("preferred_skills") or []):
            if not raw_skill:
                continue
            normalized = _norm(raw_skill)
            if normalized in seen:
                continue
            seen.add(normalized)
            counts[normalized] += 1
            display_names.setdefault(normalized, raw_skill.strip())

    user_map = {_norm(row.get("skill_name") or ""): row for row in user_skills if row.get("skill_name")}
    results: list[SkillDemand] = []
    for normalized, count in counts.most_common():
        user = user_map.get(normalized)
        proficiency = int(user.get("proficiency") or 0) if user else 0
        target = int(user.get("target_proficiency") or 80) if user else 80
        target = max(target, 1)
        proficiency_gap = max(0.0, (target - proficiency) / target * 100)
        demand_share = count / opportunities * 100
        gap_score = round(demand_share * 0.65 + proficiency_gap * 0.35, 2)
        results.append(SkillDemand(
            skill_name=display_names[normalized],
            demand_count=count,
            demand_share=round(demand_share, 2),
            user_proficiency=proficiency,
            target_proficiency=target,
            gap_score=gap_score,
            priority=_priority(gap_score),
        ))

    return sorted(results, key=lambda item: (item.gap_score, item.demand_share), reverse=True)


def build_market_report(demands: list[SkillDemand], opportunities: int) -> dict:
    top = [
        {
            "skill_name": item.skill_name,
            "demand_count": item.demand_count,
            "demand_share": item.demand_share,
            "gap_score": item.gap_score,
            "priority": item.priority,
        }
        for item in demands[:10]
    ]
    critical = [item.skill_name for item in demands if item.priority == "critical"][:5]
    high = [item.skill_name for item in demands if item.priority == "high"][:5]
    if critical:
        summary = f"Focus next on {', '.join(critical)}. These skills combine strong market demand with your largest proficiency gaps."
    elif high:
        summary = f"Your highest-value learning priorities are {', '.join(high)} based on the current opportunity pool."
    else:
        summary = "Your current skill profile is reasonably aligned with the observed opportunity pool; keep monitoring new demand."
    return {
        "opportunities_analyzed": opportunities,
        "top_skills": top,
        "critical_learning_priorities": critical,
        "high_learning_priorities": high,
        "summary": summary,
    }


def window_dates(days: int = 90) -> tuple[date, date]:
    end = date.today()
    return end - timedelta(days=max(days - 1, 0)), end
