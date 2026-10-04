from backend.app.research_engine import _is_target_role, _jsonld_candidates, _parse_rss, _role_category, _skills


def test_role_family_detection_covers_ai_ml_and_data_analyst() -> None:
    assert _role_category("Machine Learning Engineer Intern", "AI/ML Intern") == "AI/ML Intern"
    assert _role_category("Data Analyst Intern", "AI/ML Intern") == "Data Analyst Intern"
    assert _role_category("GenAI / LLM Intern", "AI/ML Intern") == "GenAI/LLM/RAG Intern"


def test_skill_extraction_normalizes_known_skills() -> None:
    skills = _skills("Python SQL Power BI pandas machine learning and RAG")
    assert "python" in skills
    assert "sql" in skills
    assert "power bi" in skills
    assert "pandas" in skills
    assert "machine learning" in skills
    assert "rag" in skills


def test_direct_jsonld_jobposting_is_discovered() -> None:
    html = '''
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "JobPosting",
      "title": "AI/ML Intern",
      "description": "Internship working with Python, PyTorch and machine learning.",
      "url": "/careers/ai-ml-intern",
      "datePosted": "2026-09-05",
      "hiringOrganization": {"name": "Example AI"},
      "jobLocation": {"address": {"addressLocality": "Delhi", "addressCountry": "IN"}}
    }
    </script>
    '''
    results = _jsonld_candidates(html, "https://example.com/careers", "AI/ML Intern")
    assert len(results) == 1
    assert results[0]["company_name"] == "Example AI"
    assert results[0]["url"] == "https://example.com/careers/ai-ml-intern"
    assert results[0]["location"] == "Delhi IN"
    assert "pytorch" in results[0]["skills"]


def test_rss_parser_uses_source_url_and_published_date() -> None:
    rss = b'''<?xml version="1.0"?><rss><channel><item>
      <title>Data Analyst Intern at Example</title>
      <link>https://example.com/jobs/123</link>
      <description>Internship using SQL and Excel.</description>
      <pubDate>Sat, 05 Sep 2026 10:00:00 GMT</pubDate>
    </item></channel></rss>'''
    results = _parse_rss(rss, "Data Analyst Intern", "https://example.com/feed")
    assert len(results) == 1
    assert results[0]["role_category"] == "Data Analyst Intern"
    assert results[0]["source_url"] == "https://example.com/feed"
    assert results[0]["published_at"] == "2026-09-05T10:00:00+00:00"



def test_target_role_filter_covers_data_and_ai_ml_roles_without_body_keyword_false_positives() -> None:
    assert _is_target_role("Data Analyst Intern")
    assert _is_target_role("GenAI / LLM Intern")
    assert _is_target_role("Machine Learning Research Intern")
    assert _is_target_role("Python Developer Intern")
    assert not _is_target_role("Finance Operations Intern")
    assert not _is_target_role("Human Resources Intern")


def test_jsonld_discovery_rejects_unrelated_internships_even_if_description_mentions_python() -> None:
    html = '''
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "JobPosting",
      "title": "Finance Operations Intern",
      "description": "Finance operations internship. Python knowledge is a plus.",
      "url": "/careers/finance-intern",
      "hiringOrganization": {"name": "Example Finance"}
    }
    </script>
    '''
    assert _jsonld_candidates(html, "https://example.com/careers", "AI/ML Intern") == []
