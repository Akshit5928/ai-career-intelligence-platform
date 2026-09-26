-- SQL + Power BI dashboard query set
-- Dataset: UCI Online Retail, normalized by data/ingest.py.

-- 1. Total revenue
SELECT ROUND(SUM(revenue), 2) AS total_revenue
FROM analytics.sales;

-- 2. Revenue by month
SELECT DATE_TRUNC('month', order_date) AS month,
       ROUND(SUM(revenue), 2) AS revenue
FROM analytics.sales
GROUP BY 1 ORDER BY 1;

-- 3. Revenue by country
SELECT country, ROUND(SUM(revenue), 2) AS revenue,
       COUNT(DISTINCT invoice_no) AS orders
FROM analytics.sales
GROUP BY country ORDER BY revenue DESC;

-- 4. Average order value
SELECT ROUND(SUM(revenue) / NULLIF(COUNT(DISTINCT invoice_no), 0), 2)
       AS average_order_value
FROM analytics.sales;

-- 5. Top customers
SELECT customer_id, ROUND(SUM(revenue), 2) AS revenue,
       COUNT(DISTINCT invoice_no) AS orders
FROM analytics.sales
WHERE customer_id IS NOT NULL
GROUP BY customer_id ORDER BY revenue DESC LIMIT 10;

-- 6. Monthly order volume
SELECT DATE_TRUNC('month', order_date) AS month,
       COUNT(DISTINCT invoice_no) AS orders
FROM analytics.sales
GROUP BY 1 ORDER BY 1;

-- 7. Top products
SELECT stock_code, MAX(description) AS description,
       SUM(quantity) AS units_sold,
       ROUND(SUM(revenue), 2) AS revenue
FROM analytics.sales
GROUP BY stock_code ORDER BY revenue DESC LIMIT 10;
