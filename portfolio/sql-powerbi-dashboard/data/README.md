# Dataset

## Source
UCI Machine Learning Repository — Online Retail
- 541,909 transactions
- UK-based non-store online retailer
- Period: 2010-12-01 to 2011-12-09
- License: CC BY 4.0
- DOI: 10.24432/C5BW33

Source: https://archive.ics.uci.edu/dataset/352/online+retail

The repository does not commit the 22.6 MB source workbook. Use the reproducible ingestion script to retrieve it.

The source provides InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, and Country. Revenue is derived as Quantity times UnitPrice.

Cleaning rules:
- Remove cancellation invoices for sales KPIs.
- Remove rows with non-positive Quantity or UnitPrice.
- Preserve missing CustomerID rows for transaction analysis, but exclude them from customer-level metrics.
