from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha256
from html import unescape
from urllib.parse import quote_plus, urljoin, urlparse
from urllib.request import Request, urlopen
import json
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

DIRECT_PATHS = ("/careers", "/jobs", "/internships", "/opportunities", "/career", "/jobs/internships")
DISCOVERY_TERMS = ("intern", "internship", "trainee", "fellow", "careers", "jobs", "opportunit")


def _fetch(url: str, timeout: int = 20) -> bytes:
    req = Request(url, headers={"User-Agent": "AI-Career-Intelligence/2.0"})
    with urlopen(req, timeout=timeout) as response:
        return response.read()


def _clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", unescape(value or "")).strip()


def _is_internship(text: str) -> bool:
    return bool(re.search(r"intern(ship)?|trainee|fellow", text, flags=re.I))


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
    for pattern in (r"\s+at\s+(.+)$", r"\s+[-|–]\s+(.+)$"):
        match = re.search(pattern, title, flags=re.I)
        if match:
            return _clean(match.group(1))
    return "Unknown company"


def _candidate(title: str, url: str, raw_text: str, fallback_role: str, source_url: str, company: str | None = None) -> dict:
    title = _clean(title)
    blob = _clean(f"{title} {raw_text}")
    return {
        "external_id": sha256(url.encode()).hexdigest()[:40],
        "title": title,
        "company_name": _clean(company) or _company_from_title(title),
        "location": "India / Remote",
        "url": url,
        "raw_text": blob[:20000],
        "published_at": None,
        "role_category": _role_category(title, fallback_role),
        "skills": _skills(blob),
        "source_url": source_url,
    }


def _parse_rss(xml_bytes: bytes, fallback_role: str, source_url: str) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    results = []
    for item in root.findall(".//item"):
        title = _clean(item.findtext("title"))
        link = _clean(item.findtext("link"))
        description = _clean(item.findtext("description"))
        pub = _clean(item.findtext("pubDate"))
        if not title or not link or not _is_internship(f"{title} {description}"):
            continue
        try:
            published = parsedate_to_datetime(pub).astimezone(timezone.utc).isoformat() if pub else None
        except (TypeError, ValueError):
            published = None
        item_data = _candidate(title, link, description, fallback_role, source_url)
        item_data["published_at"] = published
        results.append(item_data)
    return results


def _jsonld_objects(html: str) -> list[dict]:
    objects: list[dict] = []
    pattern = r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    for raw in re.findall(pattern, html, flags=re.I | re.S):
        try:
            value = json.loads(unescape(raw.strip()))
        except (json.JSONDecodeError, TypeError):
            continue
        values = value if isinstance(value, list) else [value]
        for obj in values:
            if not isinstance(obj, dict):
                continue
            objects.append(obj)
            if isinstance(obj.get("@graph"), list):
                objects.extend(x for x in obj["@graph"] if isinstance(x, dict))
    return objects


def _jsonld_candidates(html: str, page_url: str, fallback_role: str) -> list[dict]:
    results = []
    for obj in _jsonld_objects(html):
        kinds = obj.get("@type")
        kinds = kinds if isinstance(kinds, list) else [kinds]
        if "JobPosting" not in kinds:
            continue
        title = _clean(obj.get("title") or obj.get("name"))
        description = _clean(obj.get("description"))
        if not title or not _is_internship(f"{title} {description}"):
            continue
        org = obj.get("hiringOrganization") or {}
        company = org.get("name") if isinstance(org, dict) else None
        location = obj.get("jobLocation") or {}
        address = location.get("address") if isinstance(location, dict) else {}
        location_text = _clean(" ".join(str(address.get(k) or "") for k in ("addressLocality", "addressRegion", "addressCountry"))) if isinstance(address, dict) else ""
        item = _candidate(title, urljoin(page_url, _clean(obj.get("url")) or page_url), description, fallback_role, page_url, company)
        if location_text:
            item["location"] = location_text
        item["published_at"] = _clean(obj.get("datePosted")) or None
        results.append(item)
    return results


def _links(html: str, page_url: str) -> list[str]:
    found = []
    for href, anchor in re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, flags=re.I | re.S):
        url = urljoin(page_url, href)
        text = _clean(re.sub(r"<[^>]+>", " ", anchor))
        if urlparse(url).scheme in ("http", "https") and any(t in (text + " " + url).lower() for t in DISCOVERY_TERMS):
            found.append(url)
    return list(dict.fromkeys(found))[:80]


def _direct_source_candidates(source: dict, fallback_role: str) -> list[dict]:
    base = source["base_url"].rstrip("/") + "/"
    pages = [base] + [urljoin(base, path.lstrip("/")) for path in DIRECT_PATHS]
    results: list[dict] = []
    visited: set[str] = set()
    for page_url in pages:
        if page_url in visited:
            continue
        visited.add(page_url)
        try:
            html = _fetch(page_url).decode("utf-8", errors="ignore")
        except Exception:
            continue
        results.extend(_jsonld_candidates(html, page_url, fallback_role))
        for linked in _links(html, page_url):
            if linked in visited or len(visited) >= 120:
                continue
            visited.add(linked)
            try:
                child = _fetch(linked, timeout=12).decode("utf-8", errors="ignore")
            except Exception:
                continue
            results.extend(_jsonld_candidates(child, linked, fallback_role))
            if _is_internship(_clean(re.sub(r"<[^>]+>", " ", child))):
                title_match = re.search(r"<title[^>]*>(.*?)</title>", child, flags=re.I | re.S)
                title = _clean(title_match.group(1)) if title_match else "Internship opportunity"
                if _is_internship(title + " " + child[:6000]):
                    results.append(_candidate(title, linked, child[:12000], fallback_role, page_url, source.get("name")))
    unique = {item["external_id"]: item for item in results}
    return list(unique.values())


def _persist_candidates(db, run_id: str, source_id: str | None, candidates: list[dict]) -> int:
    new = 0
    now = datetime.now(timezone.utc).isoformat()
    for candidate in candidates:
        existing = db.table("research_candidates").select("id").eq("external_id", candidate["external_id"]).limit(1).execute().data or []
        if existing:
            db.table("research_candidates").update({"discovered_at": now, "processing_status": "processed"}).eq("id", existing[0]["id"]).execute()
            continue
        db.table("research_candidates").insert({
            "research_run_id": run_id, "source_id": source_id, "external_id": candidate["external_id"],
            "title": candidate["title"], "company_name": candidate["company_name"], "location": candidate["location"],
            "url": candidate["url"], "raw_text": candidate["raw_text"], "published_at": candidate["published_at"],
            "processing_status": "new",
        }).execute()
        _upsert_opportunity(db, candidate, source_id)
        new += 1
    return new


def run_research() -> dict:
    db = get_supabase()
    sources = db.table("research_sources").select("id,name,base_url,source_type,enabled,priority").eq("enabled", True).order("priority", desc=True).execute().data or []
    total_found = total_new = 0
    errors: list[str] = []
    source_results = []

    # V2: direct-source scanning is now the primary path. Each configured source gets
    # its own auditable research_run. Broad search remains a fallback for dynamic/blocked sites.
    for source in sources:
        name = source.get("name") or "unknown source"
        run = db.table("research_runs").insert({"source_id": source.get("id"), "status": "running"}).execute().data[0]
        found = new = 0
        source_errors = []
        try:
            fallback = "Research Intern - AI/ML" if source.get("source_type") == "research" else "AI/ML Intern"
            candidates = _direct_source_candidates(source, fallback)
            found = len(candidates)
            new = _persist_candidates(db, run["id"], source.get("id"), candidates)
            db.table("research_runs").update({
                "finished_at": datetime.now(timezone.utc).isoformat(), "status": "completed",
                "opportunities_found": found, "opportunities_new": new,
            }).eq("id", run["id"]).execute()
        except Exception as exc:
            source_errors.append(str(exc))
            db.table("research_runs").update({
                "finished_at": datetime.now(timezone.utc).isoformat(), "status": "failed",
                "opportunities_found": found, "opportunities_new": new, "error_message": str(exc),
            }).eq("id", run["id"]).execute()
        total_found += found
        total_new += new
        errors.extend(f"{name}: {e}" for e in source_errors)
        source_results.append({"source": name, "found": found, "new": new, "errors": source_errors})

    # Google News fallback only when explicitly configured as a source.
    fallback_source = next((s for s in sources if "google" in (s.get("name") or "").lower()), None)
    if fallback_source:
        run = db.table("research_runs").insert({"source_id": fallback_source.get("id"), "status": "running"}).execute().data[0]
        found = new = 0
        fallback_errors = []
        try:
            for role, query in ROLE_QUERIES.items():
                feed_url = "https://news.google.com/rss/search?q=" + quote_plus(query) + "&hl=en-IN&gl=IN&ceid=IN:en"
                try:
                    candidates = _parse_rss(_fetch(feed_url), role, feed_url)
                except Exception as exc:
                    fallback_errors.append(f"{role}: {exc}")
                    continue
                found += len(candidates)
                new += _persist_candidates(db, run["id"], fallback_source.get("id"), candidates)
            db.table("research_runs").update({
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "status": "completed_with_errors" if fallback_errors else "completed",
                "opportunities_found": found, "opportunities_new": new,
                "error_message": " | ".join(fallback_errors) if fallback_errors else None,
            }).eq("id", run["id"]).execute()
        except Exception as exc:
            fallback_errors.append(str(exc))
            db.table("research_runs").update({"finished_at": datetime.now(timezone.utc).isoformat(), "status": "failed", "error_message": str(exc)}).eq("id", run["id"]).execute()
        total_found += found
        total_new += new
        errors.extend(f"Google News fallback: {e}" for e in fallback_errors)

    return {"found": total_found, "new": total_new, "errors": errors, "sources": source_results, "mode": "direct-source-v2"}


def _upsert_opportunity(db, candidate: dict, source_id: str | None) -> None:
    existing = db.table("internships").select("id").eq("external_id", candidate["external_id"]).limit(1).execute().data or []
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "company_name": candidate["company_name"], "role_title": candidate["title"],
        "role_category": candidate["role_category"], "location": candidate["location"],
        "work_mode": "remote/unknown", "required_skills": candidate["skills"], "preferred_skills": [],
        "application_url": candidate["url"], "source_url": candidate["source_url"], "source_type": "direct_source",
        "relocation_possible": True, "status": "active", "last_seen_at": now, "last_verified_at": now,
        "source_confidence": 75, "external_id": candidate["external_id"],
    }
    if existing:
        internship_id = existing[0]["id"]
        db.table("internships").update(payload).eq("id", internship_id).execute()
    else:
        internship_id = db.table("internships").insert(payload).execute().data[0]["id"]
    if source_id:
        db.table("internship_sources").upsert({"internship_id": internship_id, "source_id": source_id, "source_record_url": candidate["url"]}).execute()
    db.table("research_candidates").update({"processed_at": now, "processing_status": "processed"}).eq("external_id", candidate["external_id"]).execute()
