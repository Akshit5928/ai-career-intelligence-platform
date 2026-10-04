# SQL + Power BI Internship Dashboard

## Goal
A portfolio-ready analytics project demonstrating SQL, Python/Pandas data cleaning, KPI design, and Power BI-style business reporting.

## Dataset
UCI Machine Learning Repository — Online Retail: 541,909 transactions from 2010-12-01 through 2011-12-09. The source contains invoice, product, quantity, timestamp, price, customer, and country fields. Revenue is derived as quantity times unit price. The dataset is licensed CC BY 4.0.

Source: https://archive.ics.uci.edu/dataset/352/online+retail

## Deliverables
- Reproducible UCI ingestion and cleaning script
- Transactional PostgreSQL/Supabase CSV loader
- PostgreSQL analytics schema and seven business queries
- Power BI dashboard specification
- Verified business insights from the real UCI dataset
- Automated ingestion, SQL, and analysis tests

## Latest verified analysis snapshot
The real-data smoke test in [GitHub Actions CI run #129](https://github.com/Akshit5928/ai-career-intelligence-platform/actions/runs/37185919006), on analysis commit `06a0e5ea75021b4ece4ea9e906299fa9f1d75fa5`, emitted:
- 530,104 cleaned transaction rows
- 19,960 distinct orders
- 10,666,684.54 total revenue
- 534.40 average order value
- 38 countries and 4,338 distinct customers with an ID
- November 2011 as the peak month with 1,509,496.33 revenue
- United Kingdom revenue of 9,025,222.08 (84.61% of total), across 18,019 distinct orders
- Top customer 14646 with 280,206.02 revenue across 73 orders
- Top product SKU DOT (DOTCOM POSTAGE), 706 units and 206,248.77 revenue

Full CI run #129 passed on the current branch head: lint, 11 portfolio tests, the real-data analysis smoke test, 14 main tests, and frontend build. During validation, CI exposed two workflow setup defects: the npm cache referenced a nonexistent lockfile, and the frontend job lacked its own checkout step. Both were fixed and verified by the passing run.

## Reproducible workflow

From this project directory:

```powershell
python -m pip install -r data/requirements.txt
python data/ingest.py
python data/analyze.py
```

To load the cleaned CSV into PostgreSQL or a Supabase PostgreSQL database, set `DATABASE_URL` to its connection string, then run:

```powershell
python data/load_postgres.py
```

You may pass a different cleaned CSV with `--csv path/to/file.csv`. The loader creates the schema, migrates the legacy `order_date` column name when needed, and replaces the contents of `analytics.sales` inside a transaction. Use a dedicated analytics table; this is a full table replacement. Keep credentials in environment variables and never commit them.

Run offline tests:

```powershell
pytest tests
```

The SQL tests execute all seven query statements against a disposable DuckDB fixture and reconcile core SQL KPIs with the Python analysis. This is a compatibility fixture, not a substitute for testing against a live PostgreSQL instance before production use.

## Internship relevance
Targets entry-level requirements around Python/Pandas, SQL, data cleaning, database loading, dashboarding, business insights, testing, documentation, and reproducible analysis.
