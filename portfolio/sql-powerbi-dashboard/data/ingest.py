from pathlib import Path
import pandas as pd
from ucimlrepo import fetch_ucirepo

OUT = Path(__file__).parent / "processed"
OUT.mkdir(exist_ok=True)

def load_and_clean() -> pd.DataFrame:
    dataset = fetch_ucirepo(id=352)
    df = dataset.data.features.copy()
    column_map = {
        "InvoiceNo": "invoice_no",
        "StockCode": "stock_code",
        "Description": "description",
        "Quantity": "quantity",
        "InvoiceDate": "invoice_date",
        "UnitPrice": "unit_price",
        "CustomerID": "customer_id",
        "Country": "country",
    }
    df = df.rename(columns={c: column_map.get(c, c.strip().lower().replace(" ", "_")) for c in df.columns})
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").astype("Int64")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["revenue"] = df["quantity"] * df["unit_price"]
    df = df[~df["invoice_no"].astype(str).str.upper().str.startswith("C")]
    df = df[df["quantity"] > 0]
    df = df.dropna(subset=["invoice_date", "unit_price"])
    df = df[df["unit_price"] > 0]
    return df.reset_index(drop=True)

if __name__ == "__main__":
    cleaned = load_and_clean()
    output = OUT / "online_retail_clean.csv"
    cleaned.to_csv(output, index=False)
    print(f"Wrote {len(cleaned):,} rows to {output}")
