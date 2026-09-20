import pandas as pd

from cleaning import missing_value_report, remove_duplicate_rows, standardize_column_names


def test_standardize_column_names():
    df = pd.DataFrame({"Customer Name": ["A"], "Total-Sales($)": [10]})
    out = standardize_column_names(df)
    assert list(out.columns) == ["customer_name", "total_sales"]


def test_remove_duplicate_rows():
    df = pd.DataFrame({"id": [1, 1, 2], "value": [10, 10, 20]})
    assert len(remove_duplicate_rows(df)) == 2


def test_missing_value_report():
    df = pd.DataFrame({"a": [1, None, 3], "b": [1, 2, 3]})
    report = missing_value_report(df)
    assert report.loc["a", "missing_count"] == 1
    assert report.loc["a", "missing_pct"] == 33.33
