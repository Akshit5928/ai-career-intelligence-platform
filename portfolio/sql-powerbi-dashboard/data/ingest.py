from pathlib import Path
import re

import pandas as pd
from ucimlrepo import fetch_ucirepo

OUT = Path(__file__).parent / "processed"
OUT.mkdir(exist_ok=True)


def _canonical_column(column: object) -> str:
    """Normalize UCI column labels, including whitespace/casing variations."""
    key = re.sub(r"[^a-z0-9]", "", str(column).lower())
    aliases = {
        "invoiceno": "invoice_no",
        "stockcode": "stock_code",
        "description": "description",
        "quantity": "quantity",
        "invoicedate": "invoice_date",
        "unitprice": "unit_price",
        "customerid": "customer_id",
        "country": "country",
    }
    return aliases.get(key, str(column).strip().lower().replace(" ", "_"))


def load_and_clean() -> pd.DataFrame:
    dataset = fetch_ucirepo(id=352)
    # Product identifiers are required downstream. Customer IDs and descriptions
    # are nullable in the SQL schema, so their source columns may be absent.
    required = {
        "invoice_no",
        "stock_code",
        "quantity",
        "invoice_date",
        "unit_price",
        "country",
    }

    # UCI marks InvoiceNo and StockCode as IDs, so they may be excluded from
    # data.features. Prefer the complete original frame for transaction analysis.
    df = dataset.data.original.copy() if hasattr(dataset.data, "original") else dataset.data.features.copy()
    df = df.rename(columns={column: _canonical_column(column) for column in df.columns})
    missing = required - set(df.columns)
    if missing and hasattr(dataset.data, "features"):
        feature_df = dataset.data.features.copy()
        feature_df = feature_df.rename(columns={column: _canonical_column(column) for column in feature_df.columns})
        missing_from_features = required - set(feature_df.columns)
        if len(missing_from_features) < len(missing):
            df = feature_df
            missing = missing_from_features
    if missing:
        raise ValueError(f"UCI Online Retail dataset is missing columns: {sorted(missing)}")

    if "customer_id" not in df.columns:
        df["customer_id"] = pd.NA
    if "description" not in df.columns:
        df["description"] = pd.NA

    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").astype("Int64")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["revenue"] = df["quantity"] * df["unit_price"]

    # Match the SQL schema's NOT NULL dimensions before exporting/loading.
    df = df.dropna(
        subset=["invoice_no", "stock_code", "quantity", "invoice_date", "unit_price", "country"]
    )
    df = df[~df["invoice_no"].astype(str).str.upper().str.startswith("C")]
    df = df[df["quantity"] > 0]
    df = df[df["unit_price"] > 0]
    return df.reset_index(drop=True)


if __name__ == "__main__":
    cleaned = load_and_clean()
    output = OUT / "online_retail_clean.csv"
    cleaned.to_csv(output, index=False)
    print(f"Wrote {len(cleaned):,} rows to {output}")
