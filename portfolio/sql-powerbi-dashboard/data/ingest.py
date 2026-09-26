from pathlib import Path
import pandas as pd

RAW = Path(__file__).parent / "raw"
OUT = Path(__file__).parent / "processed"
RAW.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)

def load_and_clean(source_path: str) -> pd.DataFrame:
    df = pd.read_excel(source_path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").astype("Int64")
    df["revenue"] = df["quantity"] * df["unit_price"]
    df = df[~df["invoice_no"].astype(str).str.upper().str.startswith("C")]
    df = df[df["quantity"] > 0]
    df = df[df["unit_price"] > 0]
    return df.reset_index(drop=True)

if __name__ == "__main__":
    source = RAW / "Online Retail.xlsx"
    cleaned = load_and_clean(str(source))
    output = OUT / "online_retail_clean.csv"
    cleaned.to_csv(output, index=False)
    print(f"Wrote {len(cleaned):,} rows to {output}")
