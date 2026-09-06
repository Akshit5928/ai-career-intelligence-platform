from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import re

from backend.app.research_engine import (
    _candidate,
    _clean,
    _fetch,
    _is_internship,
    _jsonld_candidates,
    _links,
)


@dataclass(frozen=True)
class SourceAdapter:
    key: str
    paths: tuple[str, ...]
    max_pages: int = 35
    confidence: int = 75


ADAPTERS: dict[str, SourceAdapter] = {
    "Unstop": SourceAdapter("unstop", ("/internships", "/jobs", "/work-from-home-jobs", "/opportunities"), 45, 90),
    "Internshala": SourceAdapter("internshala", ("/internships/", "/internships/work-from-home-jobs/", "/internships/keywords-machine-learning-internship/", "/internships/keywords-data-science-internship/", "/internships/keywords-data-analyst-internship/"), 45, 90),
    "AICTE Internship Portal": SourceAdapter("aicte", ("/internship-portal/", "/internship/", "/search/"), 35, 95),
    "LinkedIn Jobs": SourceAdapter("linkedin", ("/jobs/search/?keywords=machine%20learning%20intern", "/jobs/search/?keywords=data%20analyst%20intern", "/jobs/search/?keywords=artificial%20intelligence%20intern"), 20, 85),
    "Indeed India": SourceAdapter("indeed", ("/jobs?q=machine+learning+intern&l=India", "/jobs?q=data+analyst+intern&l=India", "/jobs?q=data+science+intern&l=India"), 25, 85),
    "Naukri": SourceAdapter("naukri", ("/machine-learning-internship-jobs", "/data-analyst-internship-jobs", "/data-science-internship-jobs"), 25, 85),
    "Wellfound": SourceAdapter("wellfound", ("/jobs", "/jobs?query=machine%20learning%20intern", "/jobs?query=data%20science%20intern"), 30, 85),
    "Google Careers": SourceAdapter("google", ("/jobs/results/?q=intern",), 30, 95),
    "Microsoft Careers": SourceAdapter("microsoft", ("/search-results.aspx?k=intern",), 30, 95),
    "Amazon Jobs India": SourceAdapter("amazon", ("/en/search?base_query=intern&loc_query=India",), 30, 95),
    "Adobe Careers": SourceAdapter("adobe", ("/en/search-results?keywords=intern",), 25, 95),
    "IBM Careers": SourceAdapter("ibm", ("/en/jobs/search?field_keyword=intern",), 25, 95),
    "Oracle Careers": SourceAdapter("oracle", ("/en/sites/jobsearch/jobs?keyword=intern",), 25, 95),
    "SAP Careers": SourceAdapter("sap", ("/search/?q=intern",), 25, 95),
    "Accenture Careers India": SourceAdapter("accenture", ("/in-en/careers/jobsearch?jk=intern",), 25, 95),
    "Deloitte Careers India": SourceAdapter("deloitte", ("/en-in/careers/search-jobs",), 25, 90),
    "EY Careers India": SourceAdapter("ey", ("/en_in/careers/search-jobs",), 25, 90),
    "KPMG Careers India": SourceAdapter("kpmg", ("/in/en/home/careers/search.html?keyword=intern",), 25, 90),
    "TCS Careers": SourceAdapter("tcs", ("/careers/india",), 25, 90),
    "Infosys Careers": SourceAdapter("infosys", ("/careers/job-search",), 25, 90),
    "Wipro Careers": SourceAdapter("wipro", ("/careers",), 25, 90),
    "HCLTech Careers": SourceAdapter("hcl", ("/careers",), 25, 90),
    "Walmart Global Tech India": SourceAdapter("walmart", ("/content/walmart-global-tech/en_us/careers.html",), 25, 90),
    "Flipkart Careers": SourceAdapter("flipkart", ("/content/careers/job-search.html",), 25, 90),
    "Meesho Careers": SourceAdapter("meesho", ("/jobs",), 25, 90),
    "Swiggy Careers": SourceAdapter("swiggy", ("/careers/",), 25, 90),
    "Zomato Careers": SourceAdapter("zomato", ("/careers",), 25, 90),
    "Zepto Careers": SourceAdapter("zepto", ("/careers",), 25, 90),
    "Razorpay Careers": SourceAdapter("razorpay", ("/jobs/",), 25, 90),
    "CRED Careers": SourceAdapter("cred", ("/careers/",), 25, 90),
    "PhonePe Careers": SourceAdapter("phonepe", ("/careers/",), 25, 90),
    "Dream11 Careers": SourceAdapter("dream11", ("/careers",), 25, 85),
    "Myntra Careers": SourceAdapter("myntra", ("/careers/",), 25, 90),
    "Newton School of Technology": SourceAdapter("newton", ("/newton-school-of-technology/", "/careers/", "/internships/", "/placements/"), 30, 80),
    "Scaler School of Technology": SourceAdapter("scaler", ("/school-of-technology/", "/careers/", "/jobs/"), 30, 80),
}


def adapter_for(source: dict) -> SourceAdapter:
    return ADAPTERS.get(source.get("name"), SourceAdapter("generic", ("/careers", "/jobs", "/internships", "/opportunities", "/career"), 30, 75))


def _looks_like_job_card(text: str) -> bool:
    lowered = text.lower()
    role_terms = ("ai", "machine learning", "data analyst", "data science", "software engineer", "mlops", "generative ai", "llm")
    return _is_internship(text) and any(term in lowered for term in role_terms)


def _html_card_candidates(html: str, page_url: str, fallback_role: str, company: str) -> list[dict]:
    results: list[dict] = []
    blocks = re.findall(r'<(?:article|li|div)[^>]*>(.*?)</(?:article|li|div)>', html, flags=re.I | re.S)
    for block in blocks[:250]:
        text = _clean(re.sub(r"<[^>]+>", " ", block))
        if not text or len(text) < 20 or len(text) > 1800 or not _looks_like_job_card(text):
            continue
        hrefs = re.findall(r'<a[^>]+href=["\']([^"\']+)["\']', block, flags=re.I)
        if not hrefs:
            continue
        link = urljoin(page_url, hrefs[0])
        if urlparse(link).scheme not in ("http", "https"):
            continue
        title_match = re.search(r'<(?:h1|h2|h3|h4|a)[^>]*>(.*?)</(?:h1|h2|h3|h4|a)>', block, flags=re.I | re.S)
        title = _clean(re.sub(r"<[^>]+>", " ", title_match.group(1))) if title_match else text[:180]
        results.append(_candidate(title, link, text, fallback_role, page_url, company))
    return results


def scan_source(source: dict, fallback_role: str) -> tuple[list[dict], list[str]]:
    adapter = adapter_for(source)
    base = source["base_url"].rstrip("/") + "/"
    pages = [urljoin(base, path.lstrip("/")) for path in adapter.paths]
    if base not in pages:
        pages.insert(0, base)
    pages = list(dict.fromkeys(pages))[: adapter.max_pages]
    results: list[dict] = []
    errors: list[str] = []
    visited: set[str] = set()
    company = source.get("name") or "Unknown company"

    for page_url in pages:
        if page_url in visited or len(visited) >= adapter.max_pages:
            continue
        visited.add(page_url)
        try:
            html = _fetch(page_url, timeout=18).decode("utf-8", errors="ignore")
        except Exception as exc:
            errors.append(f"{page_url}: {type(exc).__name__}")
            continue
        results.extend(_jsonld_candidates(html, page_url, fallback_role))
        results.extend(_html_card_candidates(html, page_url, fallback_role, company))
        for linked in _links(html, page_url):
            if linked in visited or len(visited) >= adapter.max_pages:
                continue
            if urlparse(linked).netloc != urlparse(base).netloc:
                continue
            visited.add(linked)
            try:
                child = _fetch(linked, timeout=12).decode("utf-8", errors="ignore")
            except Exception as exc:
                errors.append(f"{linked}: {type(exc).__name__}")
                continue
            results.extend(_jsonld_candidates(child, linked, fallback_role))
            results.extend(_html_card_candidates(child, linked, fallback_role, company))

    unique = {item["external_id"]: item for item in results if item.get("title")}
    return list(unique.values()), errors
