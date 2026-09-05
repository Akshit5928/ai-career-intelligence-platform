from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha256
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
import re
import xml.etree.ElementTree as ET

from backend.app.db import get_supabase

ROLE_QUERIES = {
    "AI/ML Intern": '"AI ML internship" OR "machine learning internship" India',
    "AI Engineer Intern": '"AI engineer internship" India',
    "Data Science Intern": '"data science internship" India',
    "Data Analyst Intern": '"data analyst internship" India',
    "GenAI/LLM/RAG Intern": '"GenAI internship" OR "LLM internship" OR "RAG internship" India',
    "Software Engineering Intern": '"software engineering internship" Python India',
    "Research Intern - AI/ML": '"AI ML research internship" India',
    "MLOps/Applied AI Intern": '"MLOps internship" OR "applied AI internship" India',
}

SKILL_PATTERNS = [
    "python", "sql", "excel", "power bi", "pandas", "numpy", "statistics", "machine learning",
    "deep learning", "pytorch", "tensorflow", "scikit-learn", "nlp", "computer vision",
    "transformers", "bert", "llm", "generative ai", "rag", "langchain", "llamaindex",
    "hugging face", "vector search", "fastapi", "docker", "mlops", "model evaluation",
    "prompt engineering", "agents", "agentic ai", "rest api", "git/github", "data analysis",
]


def _fetch(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "AI-Career-Intelligence/1.0"})
    with urlopen(req, timeout=20) as response:
        return response.read()


def _clean(value: str | None) -> str:
    return re.sub(r"\\s+", " ", value or "").strip()


def _role_category(title: str, fallback: str) -> str:
    text = title.lower()
    if "data analyst" in text or "business analyst" in text:
        return "Data Analyst Intern"
    if "data scientist" in text or "data science" in text:
        return "Data Science Intern"
    if "research" in text and any(x in text for x in ("ai", "ml", "machine learning")):
        return "Research Intern - AI/ML"
    if "mlops" in text or "machine learning engineer" in text:
        return "AI/ML Intern"
    if "ai engineer" in text:
        return "AI Engineer Intern"
    if any(x in text for x in ("genai", "gen ai", "llm", "rag", "generative ai")):
        return "GenAI/LLM/RAG Intern"
    if "machine learning" in text or "ai/ml" in text or "artificial intelligence" in text:
        return "AI/ML Intern"
    if "software engineer" in text or "software development" in text:
        return "Software Engineering Intern"
    return fallback


def _skills(text: str) -> list[str]:
    lower = text.lower()
    return [skill for skill in SKILL_PATTERNS if re.search(r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])", lower)]


def _company_from_title(title: str) -> str:
    for pattern in (r"\\s+at\\s+(.+)$", r"\\s+[-|–]\\s+(.+)$"):
        match = re.search(pattern, title, flags=re.I)
        if match:
            return _clean(match.group(1))
    return "Unknown company"


def _parse_rss(xml_bytes: bytes, fallback_role: str, source_url: str) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    items = []
    for item in root.findall(".//item"):
        title = _clean(item.findtext("title"))
        link = _clean(item.findtext("link"))
        description = _clean(item.findtext("description"))
        pub = _clean(item.findtext("pubDate"))
        if not title or not link:
            continue
        blob = f"{title} {description}"
        if not re.search(r"intern(ship)?|trainee|fellow", blob, flags=re.I):
            continue
        try:
            published_at = parsedate_to_datetime(pub).astimezone(timezone.utc).isoformat() if pub else None
        except (TypeError, ValueError):
            published_at = None
        items.append({
            "external_id": sha256(link.encode()).hexdigest()[:40],
            "title": title,
            "company_name": _company_from_title(title),
            "location": "India / Remote",
            "url": link,
            "raw_text": blob,
            "published_at": published_at,
            "role_category": _role_category(title, fallback_role),
            "skills": _skills(blob),
            "source_url": source_url,
        })
    return items


def _google_news_url(query: str) -> str:
    return "https://news.google.com/rss/search?q=" + quote_plus(query) + "&hl=en-IN&gl=IN&ceid=IN:en"


def run_research() -> dict:
    db = get_supabase()
    sources = db.table("research_sources").select("id,name,base_url,enabled,priority").eq("enabled", True).order("priority", desc=True).execute().data or []
    source = next((s for s in sources if "google" in (s.get("name") or "").lower()), None)
    if source is None:
        source = {"id": None, "name": "Google News RSS", "base_url": "https://news.google.com/"}

    run = db.table("research_runs").insert({"source_id": source.get("id"), "status": "running"}).execute().data[0]
    run_id = run["id"]
    found = 0
    new = 0
    errors = []
    try:
        for role, query in ROLE_QUERIES.items():
            feed_url = _google_news_url(query)
            try:
                candidates = _parse_rss(_fetch(feed_url), role, feed_url)
            except Exception as exc:
                errors.append(f"{role}: {exc}")
                continue
            found += len(candidates)
            for candidate in candidates:
                existing = db.table("research_candidates").select("id").eq("external_id", candidate["external_id"]).limit(1).execute().data or []
                if existing:
                    continue
                db.table("research_candidates").insert({
                    "research_run_id": run_id,
                    "source_id": source.get("id"),
                    "external_id": candidate["external_id"],
                    "title": candidate["title"],
                    "company_name": candidate["company_name"],
                    "location": candidate["location"],
                    "url": candidate["url"],
                    "raw_text": candidate["raw_text"],
                    "published_at": candidate["published_at"],
                    "processing_status": "new",
                }).execute()
                _upsert_opportunity(db, candidate, source.get("id"))
                new += 1

        db.table("research_runs").update({
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed_with_errors" if errors else "completed",
            "opportunities_found": found,
            "opportunities_new": new,
            "error_message": " | ".join(errors) if errors else None,
        }).eq("id", run_id).execute()
        return {"run_id": run_id, "found": found, "new": new, "errors": errors}
    except Exception as exc:
        db.table("research_runs").update({"finished_at": datetime.now(timezone.utc).isoformat(), "status": "failed", "error_message": str(exc)}).eq("id", run_id).execute()
        raise


def _upsert_opportunity(db, candidate: dict, source_id: str | None) -> None:
    existing = db.table("internships").select("id").eq("external_id", candidate["external_id"]).limit(1).execute().data or []
    payload = {
        "company_name": candidate["company_name"], "role_title": candidate["title"],
        "role_category": candidate["role_category"], "location": candidate["location"],
        "work_mode": "remote/unknown", "required_skills": candidate["skills"],
        "preferred_skills": [], "application_url": candidate["url"], "source_url": candidate["url"],
        "source_type": "job_board", "relocation_possible": True, "status": "active",
        "last_seen_at": datetime.now(timezone.utc).isoformat(),
        "last_verified_at": datetime.now(timezone.utc).isoformat(), "source_confidence": 55,
        "external_id": candidate["external_id"],
    }
    if existing:
        internship_id = existing[0]["id"]
        db.table("internships").update(payload).eq("id", internship_id).execute()
    else:
        internship_id = db.table("internships").insert(payload).execute().data[0]["id"]
    if source_id:
        db.table("internship_sources").upsert({"internship_id": internship_id, "source_id": source_id, "source_record_url": candidate["url"]}).execute()
    db.table("research_candidates").update({"processed_at": datetime.now(timezone.utc).isoformat(), "processing_status": "processed"}).eq("external_id", candidate["external_id"]).execute()
