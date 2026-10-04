# SQL + Power BI Internship Dashboard

## Goal
A portfolio-ready analytics project demonstrating SQL, Python/Pandas data cleaning, KPI design, and Power BI-style business reporting.

## Dataset
UCI Machine Learning Repository — Online Retail: 541,909 transactions from 2010-12-01 through 2011-12-09. The source contains invoice, product, quantity, timestamp, price, customer, and country fields. Revenue is derived as quantity times unit price. The dataset is licensed CC BY 4.0.

Source: https://archive.ics.uci.edu/dataset/352/online+retail

## Deliverables
- Reproducible UCI ingestion and cleaning script
- PostgreSQL/Supabase analytics table schema
- 7 SQL business queries
- Power BI dashboard specification
- Verified business insights from the real UCI dataset
- Automated tests

## Verified analysis snapshot
The CI-verified real-data analysis on commit `00a957c552953a705e15b4d70e13197ee50a04e1` produced:
- 530,104 cleaned transaction rows
- 19,960 distinct orders
- 10,666,684.54 total revenue
- 534.40 average order value
- 38 countries
- November 2011 as the peak month with 1,509,496.33 revenue
- United Kingdom revenue of 9,025,222.08 (84.61% of total)
- Top customer 14646 with 280,206.02 revenue

These values are outputs of the reproducible analysis pipeline; they are not manually invented portfolio metrics.

## Workflow
1. Install the data requirements.
2. Fetch UCI dataset ID 352.
3. Apply cleaning rules and derive revenue.
4. Validate the cleaned transaction contract.
5. Create `analytics.sales` with `sql/schema.sql`, then load `data/processed/online_retail_clean.csv` into it (the ingestion script currently exports CSV; it does not connect to PostgreSQL/Supabase).
6. Execute the seven SQL business queries in `sql/queries.sql`.
7. Build the Power BI dashboard from verified outputs and document findings, limitations, and business interpretation.

## Internship relevance
Targets recurring entry-level requirements around Python/Pandas, SQL, data cleaning, dashboarding, business insights, testing, documentation, and reproducible analysis.
