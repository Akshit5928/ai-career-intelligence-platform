"""Reusable, testable data-cleaning utilities for the portfolio project."""
from __future__ import annotations

import pandas as pd


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with normalized snake_case column names."""
    out = df.copy()
    out.columns = (out.columns.astype(str).str.strip().str.lower().str.replace(r"[^a-z0-9]+", "_", regex=True).str.strip("_"))
    return out


def remove_duplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with fully duplicated rows removed."""
    return df.drop_duplicates().reset_index(drop=True)


def missing_value_report(df: pd.DataFrame) -> pd.DataFrame:
    """Return missing counts and percentages for every column."""
    report = pd.DataFrame({"missing_count": df.isna().sum(), "missing_pct": (df.isna().mean() * 100).round(2)})
    return report.sort_values("missing_count", ascending=False)
