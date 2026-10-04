import csv
import os
import sys
from pathlib import Path

import pandas as pd
import psycopg
import pytest

PROJECT_DIR = Path(__file__).parents[1]
DATA_DIR = PROJECT_DIR / "data"
SQL_PATH = PROJECT_DIR / "sql" / "queries.sql"
sys.path.insert(0, str(DATA_DIR))
import analyze  # noqa: E402
from load_postgres import load_csv  # noqa: E402


def _query_statements() -> list[str]:
    return [
        part.strip()
        for part in SQL_PATH.read_text(encoding="utf-8").split(";")
        if part.strip()
    ]


def test_postgres_loader_and_all_seven_queries(tmp_path):
    database_url = os.environ.get("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("TEST_DATABASE_URL is not set; CI supplies a disposable PostgreSQL service.")

    csv_path = tmp_path / "retail_fixture.csv"
    columns = [
        "invoice_no", "stock_code", "description", "quantity", "invoice_date",
        "unit_price", "customer_id", "country", "revenue",
    ]
    rows = [
        ["10001", "A", "Alpha", 2, "2011-01-01 10:00:00", 5.0, 1, "United Kingdom", 10.0],
        ["10001", "B", "Beta", 1, "2011-01-01 10:00:00", 10.0, 1, "United Kingdom", 10.0],
        ["10002", "A", "Alpha", 1, "2011-02-01 10:00:00", 5.0, 2, "France", 5.0],
        ["10003", "C", "Gamma", 3, "2011-02-02 10:00:00", 4.0, "", "France", 12.0],
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)

    loaded_rows = load_csv(csv_path, database_url)
    assert loaded_rows == 4

    statements = _query_statements()
    assert len(statements) == 7
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            outputs = []
            for statement in statements:
                cur.execute(statement)
                outputs.append(cur.fetchall())

    assert float(outputs[0][0][0]) == 37.0
    assert [row[0].strftime("%Y-%m") for row in outputs[1]] == ["2011-01", "2011-02"]
    assert outputs[2][0][0] == "United Kingdom"
    assert int(outputs[2][0][2]) == 1
    assert float(outputs[3][0][0]) == 12.33
    assert outputs[4][0][0] == 1
    assert len(outputs[5]) == 2
    assert outputs[6][0][0] == "A"
    assert float(outputs[6][0][3]) == 15.0

    # Reconcile SQL output against the Python pipeline using the exact CSV fixture.
    df = pd.read_csv(csv_path, parse_dates=["invoice_date"])
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").astype("Int64")
    py = analyze.analyze(df)
    peak_month = max(outputs[1], key=lambda row: float(row[1]))
    assert py["total_revenue"] == float(outputs[0][0][0])
    assert py["orders"] == 3
    assert py["average_order_value"] == float(outputs[3][0][0])
    assert py["top_country"]["country"] == outputs[2][0][0]
    assert py["top_country"]["revenue"] == float(outputs[2][0][1])
    assert py["peak_revenue_month"]["month"] == peak_month[0].strftime("%Y-%m")
    assert py["peak_revenue_month"]["revenue"] == float(peak_month[1])
    assert py["top_customer"]["customer_id"] == outputs[4][0][0]
    assert py["top_customer"]["revenue"] == float(outputs[4][0][1])
    assert py["top_product"]["stock_code"] == outputs[6][0][0]
    assert py["top_product"]["revenue"] == float(outputs[6][0][3])
