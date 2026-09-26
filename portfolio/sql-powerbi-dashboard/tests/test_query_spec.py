from pathlib import Path

SQL_FILE = Path(__file__).parents[1] / "sql" / "queries.sql"
DASHBOARD_FILE = Path(__file__).parents[1] / "dashboard" / "dashboard_spec.md"


def test_query_file_exists():
    assert SQL_FILE.exists()


def test_query_set_has_seven_queries():
    sql = SQL_FILE.read_text(encoding="utf-8")
    assert sql.count("-- ") >= 7


def test_queries_use_documented_table():
    sql = SQL_FILE.read_text(encoding="utf-8")
    assert "analytics.sales" in sql


def test_dashboard_matches_dataset_dimensions():
    dashboard = DASHBOARD_FILE.read_text(encoding="utf-8")
    assert "Revenue by country" in dashboard
    assert "Country" in dashboard
    assert "Product / StockCode" in dashboard
    assert "Category" not in dashboard
