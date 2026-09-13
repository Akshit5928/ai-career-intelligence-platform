from urllib.parse import urljoin

from backend.app import source_adapters


def test_adapter_catalog_has_priority_sources():
    for name in (
        "Unstop",
        "Internshala",
        "AICTE Internship Portal",
        "LinkedIn Jobs",
        "Naukri",
        "Wellfound",
        "Google Careers",
        "Microsoft Careers",
        "Newton School of Technology",
        "Scaler School of Technology",
    ):
        adapter = source_adapters.adapter_for({"name": name})
        assert adapter.key != "generic"
        assert adapter.max_pages > 0
        assert 0 < adapter.confidence <= 100


def test_unknown_source_uses_safe_generic_adapter():
    adapter = source_adapters.adapter_for({"name": "Unknown Source"})
    assert adapter.key == "generic"
    assert "/internships" in adapter.paths


def test_html_card_candidate_extracts_ai_internship(monkeypatch):
    html = """
    <article>
      <h3>AI/ML Intern</h3>
      <p>Python SQL machine learning internship opportunity.</p>
      <a href="/jobs/ai-ml-intern">Apply</a>
    </article>
    """
    rows = source_adapters._html_card_candidates(
        html,
        "https://example.com/jobs",
        "AI/ML Intern",
        "Example Co",
    )
    assert len(rows) == 1
    assert rows[0]["title"] == "AI/ML Intern"
    assert rows[0]["company_name"] == "Example Co"
    assert "python" in rows[0]["skills"]
    assert "sql" in rows[0]["skills"]


def test_adapter_paths_resolve_from_site_root():
    source = {
        "name": "EY Careers India",
        "base_url": "https://www.ey.com/en_in/careers",
    }
    adapter = source_adapters.adapter_for(source)
    assert urljoin(
        source["base_url"].rstrip("/") + "/", adapter.paths[0]
    ) == "https://www.ey.com/en_in/careers"
    assert urljoin(
        source["base_url"].rstrip("/") + "/", "/en_in/careers/search-jobs"
    ) == "https://www.ey.com/en_in/careers/search-jobs"


def test_html_card_candidate_rejects_unrelated_senior_role():
    html = """
    <article>
      <h3>Senior Accountant</h3>
      <p>Internship resources and AI tools are mentioned on this page.</p>
      <a href="/jobs/accountant">Apply</a>
    </article>
    """
    rows = source_adapters._html_card_candidates(
        html,
        "https://example.com/jobs",
        "AI/ML Intern",
        "Example Co",
    )
    assert rows == []
