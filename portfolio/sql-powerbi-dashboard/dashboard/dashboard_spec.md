# Dashboard specification

## KPI cards
- Total revenue: 10,666,684.54
- Total orders: 19,960
- Average order value: 534.40
- Countries: 38
- Identified customers: 4,338

## Visuals
- Monthly revenue trend — highlight November 2011 peak
- Revenue by country — show concentration and country contribution
- Top 10 customers — identify high-value customer concentration
- Monthly order volume — compare demand volume with revenue
- Top 10 products — rank products by revenue and units sold

## Filters
- Date range
- Country
- Customer
- Product / StockCode

## Verified business insights
1. The United Kingdom generated 9,025,222.08 in revenue, representing 84.61% of total verified revenue, across 18,019 distinct orders.
2. November 2011 was the peak month at 1,509,496.33 revenue, representing 14.15% of total verified revenue.
3. Customer 14646 generated 280,206.02 in revenue (2.63% of total), across 73 distinct orders.
4. SKU DOT (DOTCOM POSTAGE) was the top product by revenue at 206,248.77, with 706 units sold.

## Verification provenance
Values above were emitted by the real UCI analysis smoke test in [CI run #119](https://github.com/Akshit5928/ai-career-intelligence-platform/actions/runs/37185811315), on analysis commit `96070eb3032d39bec9695935ef51097efdb53921`. The analysis smoke test passed. The SQL query suite runs all seven queries against a disposable DuckDB fixture and reconciles monthly revenue, monthly orders, country revenue, top customer, top product, total revenue, and AOV against Python analysis on that fixture. This is not a live PostgreSQL integration test; wait for the newest full CI run before calling the overall branch CI green.

## Data model
The dashboard is built from the cleaned UCI Online Retail transaction table. Revenue is derived as `quantity * unit_price`. The PostgreSQL loader uses a transaction and replaces all rows in `analytics.sales`; use a dedicated analytics table/database.

## Insight standard
Every published insight must be derived from verified query output. Do not invent values or conclusions. When dashboard visuals are created, retain the query/output provenance for each KPI and insight.
