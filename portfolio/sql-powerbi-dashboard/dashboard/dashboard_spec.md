# Dashboard specification

## KPI cards
- Total revenue: 10,666,684.54
- Total orders: 19,960
- Average order value: 534.40
- Countries: 38

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
1. The United Kingdom generated 9,025,222.08 in revenue, representing 84.61% of total verified revenue.
2. November 2011 was the peak month at 1,509,496.33 revenue, representing 14.15% of total verified revenue.
3. Customer 14646 generated 280,206.02 in revenue, representing 2.63% of total verified revenue.

## Data model
The dashboard is built from the cleaned UCI Online Retail transaction table. Revenue is derived as `quantity * unit_price`.

## Insight standard
Every published insight must be derived from verified query output. Do not invent values or conclusions. When dashboard visuals are created, retain the query/output provenance for each KPI and insight.
