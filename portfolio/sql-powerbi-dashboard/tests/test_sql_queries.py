from pathlib import Path
import sys

import duckdb
import pandas as pd

PROJECT_DIR = Path(__file__).parents[1]
SQL_PATH = PROJECT_DIR / "sql" / "queries.sql"


def _query_statements() -> list[str]:
    raw = SQL_PATH.read_text(encoding="utf-8")
    return [part.strip() for part in raw.split(";") if part.strip()]


def _fixture_connection():
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE SCHEMA analytics")
    conn.execute("""
        CREATE TABLE analytics.sales (
            invoice_no VARCHAR NOT NULL, stock_code VARCHAR NOT NULL,
            description VARCHAR, quantity INTEGER NOT NULL,
            invoice_date TIMESTAMP NOT NULL, unit_price DECIMAL(12, 4) NOT NULL,
            customer_id BIGINT, country VARCHAR NOT NULL,
            revenue DECIMAL(14, 4) NOT NULL
        )
    """)
    conn.execute("""
        INSERT INTO analytics.sales VALUES
        ('10001', 'A', 'Alpha', 2, '2011-01-01 10:00:00', 5.0, 1, 'United Kingdom', 10.0),
        ('10001', 'B', 'Beta', 1, '2011-01-01 10:00:00', 10.0, 1, 'United Kingdom', 10.0),
        ('10002', 'A', 'Alpha', 1, '2011-02-01 10:00:00', 5.0, 2, 'France', 5.0),
        ('10003', 'C', 'Gamma', 3, '2011-02-02 10:00:00', 4.0, NULL, 'France', 12.0)
    """)
    return conn


def test_all_seven_business_queries_execute_and_return_expected_results():
    statements = _query_statements()
    assert len(statements) == 7, f"Expected 7 SQL queries, found {len(statements)}"
    conn = _fixture_connection()
    try:
        results = [conn.execute(statement).fetchall() for statement in statements]
    finally:
        conn.close()

    assert float(results[0][0][0]) == 37.0
    assert len(results[1]) == 2
    assert results[2][0][0] == "United Kingdom"
    assert int(results[2][0][2]) == 1
    assert float(results[3][0][0]) == 12.33
    assert results[4][0][0] == 1
    assert len(results[5]) == 2
    assert results[6][0][0] == "A"
    assert float(results[6][0][3]) == 15.0


def test_python_analysis_matches_sql_kpis_on_same_fixture():
    sys.path.insert(0, str(PROJECT_DIR / "data"))
    import analyze  # noqa: E402

    df = pd.DataFrame([
        {"invoice_no": "10001", "stock_code": "A", "description": "Alpha", "quantity": 2, "invoice_date": pd.Timestamp("2011-01-01 10:00:00"), "unit_price": 5.0, "customer_id": 1, "country": "United Kingdom", "revenue": 10.0},
        {"invoice_no": "10001", "stock_code": "B", "description": "Beta", "quantity": 1, "invoice_date": pd.Timestamp("2011-01-01 10:00:00"), "unit_price": 10.0, "customer_id": 1, "country": "United Kingdom", "revenue": 10.0},
        {"invoice_no": "10002", "stock_code": "A", "description": "Alpha", "quantity": 1, "invoice_date": pd.Timestamp("2011-02-01 10:00:00"), "unit_price": 5.0, "customer_id": 2, "country": "France", "revenue": 5.0},
        {"invoice_no": "10003", "stock_code": "C", "description": "Gamma", "quantity": 3, "invoice_date": pd.Timestamp("2011-02-02 10:00:00"), "unit_price": 4.0, "customer_id": pd.NA, "country": "France", "revenue": 12.0},
    ])
    df["customer_id"] = df["customer_id"].astype("Int64")
    result = analyze.analyze(df)
    conn = _fixture_connection()
    try:
        sql_total = float(conn.execute("SELECT SUM(revenue) FROM analytics.sales").fetchone()[0])
        sql_orders = int(conn.execute("SELECT COUNT(DISTINCT invoice_no) FROM analytics.sales").fetchone()[0])
        sql_countries = int(conn.execute("SELECT COUNT(DISTINCT country) FROM analytics.sales").fetchone()[0])
    finally:
        conn.close()

    assert result["total_revenue"] == sql_total
    assert result["orders"] == sql_orders
    assert result["countries"] == sql_countries
    assert result["customers_with_id"] == 2
