"""Load the cleaned UCI retail CSV into PostgreSQL/Supabase.

Set DATABASE_URL to a PostgreSQL connection string. The load is transactional
and replaces analytics.sales contents only after schema validation succeeds.
"""
import argparse
import os
from pathlib import Path

import psycopg

DATA_DIR = Path(__file__).parent
DEFAULT_CSV = DATA_DIR / "processed" / "online_retail_clean.csv"
SCHEMA_PATH = DATA_DIR.parent / "sql" / "schema.sql"

COLUMNS = (
    "invoice_no",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "unit_price",
    "customer_id",
    "country",
    "revenue",
)


def load_csv(csv_path: Path, database_url: str) -> int:
    """Replace analytics.sales rows from a validated CSV in one transaction."""
    if not csv_path.is_file():
        raise FileNotFoundError(
            f"Cleaned CSV not found: {csv_path}. Run data/ingest.py first."
        )

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_PATH.read_text(encoding="utf-8"))

            # Migrate the previous schema's date name if this table already exists.
            cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'analytics' AND table_name = 'sales'
                """
            )
            existing = {row[0] for row in cur.fetchall()}
            if "order_date" in existing and "invoice_date" not in existing:
                cur.execute(
                    "ALTER TABLE analytics.sales RENAME COLUMN order_date TO invoice_date"
                )
                existing.remove("order_date")
                existing.add("invoice_date")

            missing = set(COLUMNS) - existing
            if missing:
                raise ValueError(
                    "analytics.sales is missing required columns: "
                    + ", ".join(sorted(missing))
                )

            column_sql = ", ".join(f'"{name}"' for name in COLUMNS)
            cur.execute("DELETE FROM analytics.sales")
            copy_sql = (
                f"COPY analytics.sales ({column_sql}) "
                "FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')"
            )
            with cur.copy(copy_sql) as copy, csv_path.open(
                "r", encoding="utf-8", newline=""
            ) as source:
                for chunk in iter(lambda: source.read(1024 * 1024), ""):
                    copy.write(chunk)

            cur.execute("SELECT COUNT(*) FROM analytics.sales")
            return int(cur.fetchone()[0])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        parser.error("Set DATABASE_URL to your PostgreSQL/Supabase connection string.")
    rows = load_csv(args.csv, database_url)
    print(f"Loaded {rows:,} rows into analytics.sales")


if __name__ == "__main__":
    main()
