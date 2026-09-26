-- SQL + Power BI dashboard query set
-- Replace analytics.sales with the final dataset table after ingestion.

-- 1. Total revenue
SELECT SUM(revenue) AS total_revenue
FROM analytics.sales;

-- 2. Revenue by month
SELECT DATE_TRUNC('month', order_date) AS month,
       SUM(revenue) AS revenue
FROM analytics.sales
GROUP BY 1
ORDER BY 1;

-- 3. Revenue by category
SELECT category,
       SUM(revenue) AS revenue,
       COUNT(*) AS orders
FROM analytics.sales
GROUP BY category
ORDER BY revenue DESC;

-- 4. Average order value
SELECT AVG(revenue) AS average_order_value
FROM analytics.sales;

-- 5. Top customers
SELECT customer_id,
       SUM(revenue) AS revenue,
       COUNT(*) AS orders
FROM analytics.sales
GROUP BY customer_id
ORDER BY revenue DESC
LIMIT 10;

-- 6. Monthly order volume
SELECT DATE_TRUNC('month', order_date) AS month,
       COUNT(*) AS orders
FROM analytics.sales
GROUP BY 1
ORDER BY 1;
