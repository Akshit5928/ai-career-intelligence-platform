from pathlib import Path
import pandas as pd
from ucimlrepo import fetch_ucirepo

OUT = Path(__file__).parent / "processed"
OUT.mkdir(exist_ok=True)

def load_and_clean() -> pd.DataFrame:
    dataset = fetch_ucirepo(id=352)
    df = dataset.data.features.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").astype("Int64")
    df["revenue"] = df["quantity"] * df["unitprice"]
    df = df[~df["invoice_no"].astype(str).str.upper().str.startswith("C")]
    df = df[df["quantity"] > 0]
    df = df[df["unitprice"] > 0]
    return df.reset_index(drop=True)

if __name__ == "__main__":
    cleaned = load_and_clean()
    output = OUT / "online_retail_clean.csv"
    cleaned.to_csv(output, index=False)
    print(f"Wrote {len(cleaned):,} rows to {output}")
