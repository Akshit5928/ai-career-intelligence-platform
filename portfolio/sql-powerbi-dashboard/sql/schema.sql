CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.sales (
    invoice_no TEXT NOT NULL,
    stock_code TEXT NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL,
    order_date TIMESTAMP NOT NULL,
    unit_price NUMERIC(12, 4) NOT NULL,
    customer_id BIGINT,
    country TEXT NOT NULL,
    revenue NUMERIC(14, 4) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sales_order_date ON analytics.sales(order_date);
CREATE INDEX IF NOT EXISTS idx_sales_customer_id ON analytics.sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_country ON analytics.sales(country);
