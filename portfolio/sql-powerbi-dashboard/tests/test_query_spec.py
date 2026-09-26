from pathlib import Path

SQL_FILE = Path(__file__).parents[1] / "sql" / "queries.sql"

def test_query_file_exists():
    assert SQL_FILE.exists()

def test_query_set_has_six_queries():
    sql = SQL_FILE.read_text(encoding="utf-8")
    assert sql.count("-- ") >= 6

def test_queries_use_documented_table():
    sql = SQL_FILE.read_text(encoding="utf-8")
    assert "analytics.sales" in sql
