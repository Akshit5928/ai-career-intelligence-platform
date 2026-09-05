from datetime import datetime, timezone

from backend.app.matching import calculate_match


NOW = datetime(2026, 9, 6, 0, 0, tzinfo=timezone.utc)


def test_data_analyst_match_identifies_gaps() -> None:
    result = calculate_match(
        user_skills=["Python", "Pandas"],
        target_roles=["Data Analyst Intern"],
        target_locations=["Delhi NCR", "India", "Remote"],
        relocation_ok=True,
        role_category="Data Analyst",
        required_skills=["Python", "SQL", "Power BI", "Excel"],
        location="Remote",
        eligibility="Freshers / entry-level",
        now=NOW,
    )
    assert result.score > 50
    assert result.missing_skills == ["SQL", "Power BI", "Excel"]
    assert result.role_score == 100
    assert result.location_score == 100


def test_strong_fit_scores_high() -> None:
    result = calculate_match(
        user_skills=["Python", "SQL", "Power BI", "Excel"],
        target_roles=["Data Analyst Intern"],
        target_locations=["India", "Remote"],
        relocation_ok=False,
        role_category="Data Analyst",
        required_skills=["Python", "SQL", "Power BI", "Excel"],
        location="Remote",
        eligibility="Students / freshers",
        deadline=datetime(2026, 9, 8, tzinfo=timezone.utc),
        now=NOW,
    )
    assert result.score >= 90
    assert result.missing_skills == []


def test_relocation_raises_nonmatching_location() -> None:
    result = calculate_match(
        user_skills=["Python"],
        target_roles=["AI/ML Intern"],
        target_locations=["Delhi NCR", "India", "Remote"],
        relocation_ok=True,
        role_category="AI/ML",
        required_skills=["Python", "Machine Learning"],
        location="Bangalore",
        eligibility="No experience required",
        now=NOW,
    )
    assert result.location_score == 60
