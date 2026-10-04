import importlib.util
from pathlib import Path

import pandas as pd

INGEST_PATH = Path(__file__).parents[1] / "data" / "ingest.py"
SPEC = importlib.util.spec_from_file_location("portfolio_ingest", INGEST_PATH)
ingest = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(ingest)


def test_cleaning_rules_without_network(monkeypatch):
    source = pd.DataFrame(
        [
            {"InvoiceNo": "10001", "StockCode": "A", "Description": "Valid", "Quantity": 2, "InvoiceDate": "2011-01-01 10:00:00", "UnitPrice": 5.0, "CustomerID": 1, "Country": "United Kingdom"},
            {"InvoiceNo": "C10002", "StockCode": "B", "Description": "Cancelled", "Quantity": 3, "InvoiceDate": "2011-01-01 11:00:00", "UnitPrice": 7.0, "CustomerID": 2, "Country": "United Kingdom"},
            {"InvoiceNo": "10003", "StockCode": "C", "Description": "Negative quantity", "Quantity": -1, "InvoiceDate": "2011-01-01 12:00:00", "UnitPrice": 8.0, "CustomerID": 3, "Country": "United Kingdom"},
            {"InvoiceNo": "10004", "StockCode": "D", "Description": "Zero price", "Quantity": 1, "InvoiceDate": "2011-01-01 13:00:00", "UnitPrice": 0.0, "CustomerID": 4, "Country": "United Kingdom"},
        ]
    )

    class Dataset:
        pass

    dataset = Dataset()
    dataset.data = Dataset()
    dataset.data.features = source
    monkeypatch.setattr(ingest, "fetch_ucirepo", lambda id: dataset)

    cleaned = ingest.load_and_clean()

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["invoice_no"] == "10001"
    assert cleaned.iloc[0]["revenue"] == 10.0
    assert cleaned.iloc[0]["customer_id"] == 1
    assert str(cleaned.iloc[0]["invoice_date"]) == "2011-01-01 10:00:00"


def test_column_normalization_handles_whitespace_and_casing(monkeypatch):
    source = pd.DataFrame(
        [{
            " InvoiceNo ": "10005",
            " StockCode ": "E",
            " Description ": "Normalized",
            " Quantity ": 4,
            " InvoiceDate ": "2011-01-02 10:00:00",
            " UnitPrice ": 2.5,
            " CustomerID ": 5,
            " Country ": "India",
        }]
    )

    class Dataset:
        pass

    dataset = Dataset()
    dataset.data = Dataset()
    dataset.data.features = source
    monkeypatch.setattr(ingest, "fetch_ucirepo", lambda id: dataset)

    cleaned = ingest.load_and_clean()

    assert cleaned.iloc[0]["invoice_no"] == "10005"
    assert cleaned.iloc[0]["stock_code"] == "E"
    assert cleaned.iloc[0]["revenue"] == 10.0


def test_cleaning_drops_rows_missing_required_schema_fields(monkeypatch):
    source = pd.DataFrame([
        {"InvoiceNo": "10006", "StockCode": None, "Description": "Missing SKU", "Quantity": 1, "InvoiceDate": "2011-01-03 10:00:00", "UnitPrice": 3.0, "CustomerID": 6, "Country": "India"},
        {"InvoiceNo": None, "StockCode": "F", "Description": "Missing invoice", "Quantity": 1, "InvoiceDate": "2011-01-03 10:00:00", "UnitPrice": 3.0, "CustomerID": 7, "Country": "India"},
        {"InvoiceNo": "10008", "StockCode": "G", "Description": "Valid", "Quantity": 2, "InvoiceDate": "2011-01-03 10:00:00", "UnitPrice": 3.0, "CustomerID": None, "Country": "India"},
    ])

    class Dataset:
        pass

    dataset = Dataset()
    dataset.data = Dataset()
    dataset.data.features = source
    monkeypatch.setattr(ingest, "fetch_ucirepo", lambda id: dataset)

    cleaned = ingest.load_and_clean()

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["invoice_no"] == "10008"
    assert pd.isna(cleaned.iloc[0]["customer_id"])
