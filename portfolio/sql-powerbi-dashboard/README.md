# SQL + Power BI Internship Dashboard

## Goal
A portfolio-ready analytics project demonstrating SQL, Python/Pandas data cleaning, KPI design, and Power BI-style business reporting.

## Dataset
UCI Machine Learning Repository — Online Retail: 541,909 transactions from 2010-12-01 through 2011-12-09. The source contains invoice, product, quantity, timestamp, price, customer, and country fields. Revenue is derived as quantity times unit price. The dataset is licensed CC BY 4.0.

Source: https://archive.ics.uci.edu/dataset/352/online+retail

## Deliverables
- Reproducible UCI ingestion and cleaning script
- Normalized PostgreSQL/Supabase schema
- 7 SQL business queries
- Power BI dashboard specification
- Three evidence-based business insights
- Automated tests

## Current status
Dataset selected and ingestion pipeline added. The runtime cannot download the source workbook directly, so the project uses UCI's documented Python loader. No business findings are claimed until data is actually loaded and query outputs are verified.

## Workflow
1. Install the data requirements.
2. Fetch UCI dataset ID 352.
3. Apply cleaning rules and derive revenue.
4. Load the processed data into PostgreSQL/Supabase.
5. Execute and validate the seven SQL queries.
6. Build the Power BI dashboard from verified outputs.
7. Document findings and limitations.

## Internship relevance
Targets recurring entry-level requirements around Python/Pandas, SQL, data cleaning, dashboarding, business insights, testing, documentation, and reproducible analysis.
