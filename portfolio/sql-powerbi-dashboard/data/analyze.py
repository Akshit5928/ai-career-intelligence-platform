from pathlib import Path
import json
import pandas as pd

from ingest import load_and_clean

OUT = Path(__file__).parent / "processed"

def analyze(df: pd.DataFrame) -> dict:
    orders = df.groupby("invoice_no", as_index=False)["revenue"].sum()
    monthly = (
        df.assign(month=df["invoice_date"].dt.to_period("M").astype(str))
        .groupby("month", as_index=False)["revenue"].sum()
    )
    country = (
        df.groupby("country", as_index=False)
        .agg(revenue=("revenue", "sum"), orders=("invoice_no", "nunique"))
        .sort_values("revenue", ascending=False)
    )
    customers = (
        df.dropna(subset=["customer_id"])
        .groupby("customer_id", as_index=False)
        .agg(revenue=("revenue", "sum"), orders=("invoice_no", "nunique"))
        .sort_values("revenue", ascending=False)
    )
    products = (
        df.groupby(["stock_code", "description"], dropna=False, as_index=False)
        .agg(units_sold=("quantity", "sum"), revenue=("revenue", "sum"))
        .sort_values("revenue", ascending=False)
    )

    peak_month = monthly.loc[monthly["revenue"].idxmax()]
    top_country = country.iloc[0]
    top_product = products.iloc[0]

    return {
        "clean_rows": int(len(df)),
        "date_min": df["invoice_date"].min().isoformat(),
        "date_max": df["invoice_date"].max().isoformat(),
        "total_revenue": round(float(df["revenue"].sum()), 2),
        "orders": int(df["invoice_no"].nunique()),
        "average_order_value": round(float(df["revenue"].sum() / df["invoice_no"].nunique()), 2),
        "countries": int(df["country"].nunique()),
        "customers_with_id": int(df["customer_id"].notna().sum()),
        "peak_revenue_month": {"month": peak_month["month"], "revenue": round(float(peak_month["revenue"]), 2)},
        "top_country": {"country": top_country["country"], "revenue": round(float(top_country["revenue"]), 2), "orders": int(top_country["orders"])},
        "top_customer": {"customer_id": int(customers.iloc[0]["customer_id"]), "revenue": round(float(customers.iloc[0]["revenue"]), 2), "orders": int(customers.iloc[0]["orders"])},
        "top_product": {"stock_code": str(top_product["stock_code"]), "description": str(top_product["description"]), "units_sold": float(top_product["units_sold"]), "revenue": round(float(top_product["revenue"]), 2)},
    }

if __name__ == "__main__":
    result = analyze(load_and_clean())
    print(json.dumps(result, indent=2))
