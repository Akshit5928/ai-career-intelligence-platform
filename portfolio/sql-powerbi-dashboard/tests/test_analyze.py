import sys
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parents[1] / "data"
sys.path.insert(0, str(DATA_DIR))
import analyze  # noqa: E402


def test_analysis_counts_unique_customers_and_groups_products_by_stock_code():
    df = pd.DataFrame(
        [
            {"invoice_no": "10001", "stock_code": "A", "description": "Alpha", "quantity": 2, "invoice_date": pd.Timestamp("2011-01-01"), "unit_price": 5.0, "customer_id": 1, "country": "United Kingdom", "revenue": 10.0},
            {"invoice_no": "10001", "stock_code": "A", "description": "Alpha updated", "quantity": 1, "invoice_date": pd.Timestamp("2011-01-01"), "unit_price": 5.0, "customer_id": 1, "country": "United Kingdom", "revenue": 5.0},
            {"invoice_no": "10002", "stock_code": "B", "description": "Beta", "quantity": 1, "invoice_date": pd.Timestamp("2011-02-01"), "unit_price": 20.0, "customer_id": 2, "country": "France", "revenue": 20.0},
            {"invoice_no": "10003", "stock_code": "C", "description": "No ID", "quantity": 1, "invoice_date": pd.Timestamp("2011-02-02"), "unit_price": 4.0, "customer_id": pd.NA, "country": "France", "revenue": 4.0},
        ]
    )
    df["customer_id"] = df["customer_id"].astype("Int64")

    result = analyze.analyze(df)

    assert result["customers_with_id"] == 2
    assert result["orders"] == 3
    assert result["top_product"]["stock_code"] == "B"
    assert result["top_product"]["revenue"] == 20.0
