from backend.app import research_v21


class _Query:
    def __init__(self, rows):
        self.rows = rows
        self.update_payload = None

    def select(self, *_args):
        return self

    def eq(self, *_args):
        return self

    def order(self, *_args, **_kwargs):
        return self

    def insert(self, payload):
        return self

    def update(self, payload):
        self.update_payload = payload
        return self

    def execute(self):
        return type("Response", (), {"data": self.rows})()


class _DB:
    def __init__(self):
        self.runs = _Query([{"id": "run-1"}])
        self.updated = []

    def table(self, name):
        if name == "research_sources":
            return _Query(
                [{
                    "id": "source-1",
                    "name": "Example source",
                    "base_url": "https://example.com",
                    "source_type": "company",
                    "enabled": True,
                    "priority": 1,
                }]
            )
        if name == "research_runs":
            q = _Query([{"id": "run-1"}])
            original_update = q.update

            def update(payload):
                self.updated.append(payload)
                return original_update(payload)

            q.update = update
            return q
        raise AssertionError(f"unexpected table: {name}")


def test_recoverable_scan_errors_persist_as_completed(monkeypatch):
    db = _DB()
    monkeypatch.setattr(research_v21, "get_supabase", lambda: db)
    monkeypatch.setattr(
        research_v21,
        "adapter_for",
        lambda _source: type("Adapter", (), {"key": "generic", "confidence": 50})(),
    )
    monkeypatch.setattr(
        research_v21,
        "scan_source",
        lambda _source, _fallback: ([{"role_title": "AI Intern"}], ["blocked"]),
    )
    monkeypatch.setattr(
        research_v21,
        "_persist_candidates",
        lambda _db, _run_id, _source_id, _candidates: 1,
    )

    result = research_v21.run_research_v21()

    assert result["found"] == 1
    assert result["new"] == 1
    assert result["errors"] == ["Example source: blocked"]
    assert db.updated == [
        {
            "finished_at": db.updated[0]["finished_at"],
            "status": "completed",
            "opportunities_found": 1,
            "opportunities_new": 1,
            "error_message": "blocked",
        }
    ]
