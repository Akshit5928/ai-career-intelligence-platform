from __future__ import annotations

from datetime import datetime, timezone

from backend.app.db import get_supabase
from backend.app.research_engine import _persist_candidates
from backend.app.source_adapters import adapter_for, scan_source


def run_research_v21() -> dict:
    """Run source-specific discovery with auditable per-source runs.

    Adapter failures are isolated per source. Dynamic/blocked sources are recorded
    instead of pretending that a zero-result scan means there are no jobs.
    """
    db = get_supabase()
    sources = (
        db.table("research_sources")
        .select("id,name,base_url,source_type,enabled,priority")
        .eq("enabled", True)
        .order("priority", desc=True)
        .execute()
        .data
        or []
    )
    total_found = total_new = 0
    errors: list[str] = []
    source_results: list[dict] = []

    for source in sources:
        name = source.get("name") or "unknown source"
        run = db.table("research_runs").insert({"source_id": source.get("id"), "status": "running"}).execute().data[0]
        found = new = 0
        adapter = adapter_for(source)
        try:
            fallback = "Research Intern - AI/ML" if source.get("source_type") in {"research", "university", "institute"} else "AI/ML Intern"
            candidates, scan_errors = scan_source(source, fallback)
            found = len(candidates)
            new = _persist_candidates(db, run["id"], source.get("id"), candidates)
            status = "completed_with_errors" if scan_errors else "completed"
            error_message = " | ".join(scan_errors[:20]) if scan_errors else None
            db.table("research_runs").update({
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "status": status,
                "opportunities_found": found,
                "opportunities_new": new,
                "error_message": error_message,
            }).eq("id", run["id"]).execute()
            errors.extend(f"{name}: {item}" for item in scan_errors[:20])
        except Exception as exc:
            error_message = f"{type(exc).__name__}: {exc}"
            errors.append(f"{name}: {error_message}")
            db.table("research_runs").update({
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "status": "failed",
                "opportunities_found": found,
                "opportunities_new": new,
                "error_message": error_message,
            }).eq("id", run["id"]).execute()
        total_found += found
        total_new += new
        source_results.append({
            "source": name,
            "adapter": adapter.key,
            "confidence": adapter.confidence,
            "found": found,
            "new": new,
        })

    return {
        "found": total_found,
        "new": total_new,
        "errors": errors,
        "sources": source_results,
        "mode": "source-specific-v2.1",
    }
