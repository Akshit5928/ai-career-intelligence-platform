CREATE SCHEMA IF NOT EXISTS analytics;

-- One row per cleaned transaction line. invoice_date matches the CSV emitted
-- by data/ingest.py, use this schema when loading online_retail_clean.csv.
CREATE TABLE IF NOT EXISTS analytics.sales (
    invoice_no TEXT NOT NULL,
    stock_code TEXT NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL,
    invoice_date TIMESTAMP NOT NULL,
    unit_price NUMERIC(12, 4) NOT NULL,
    customer_id BIGINT,
    country TEXT NOT NULL,
    revenue NUMERIC(14, 4) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sales_invoice_date ON analytics.sales(invoice_date);
CREATE INDEX IF NOT EXISTS idx_sales_customer_id ON analytics.sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_country ON analytics.sales(country);
