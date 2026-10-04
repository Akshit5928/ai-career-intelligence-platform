# Verified business insights

Analysis source: UCI Online Retail dataset (UCI dataset ID 352).

## Verification provenance

- Real-data smoke test: GitHub Actions CI run [#131](https://github.com/Akshit5928/ai-career-intelligence-platform/actions/runs/37185978283)
- Analysis commit: `15969badb1be4bf4adb91605a8daaaf901c189dc`
- Full CI run #131 passed on analysis commit `15969badb1be4bf4adb91605a8daaaf901c189dc`: lint, all 11 portfolio tests, the real UCI analysis smoke test, all 14 main tests, and frontend build.
- SQL business-query tests execute all seven queries against a disposable DuckDB fixture. This validates query syntax and aggregation behavior in that fixture; it is not a live PostgreSQL integration test.

## Verified outputs

| Metric | Verified value |
|---|---:|
| Cleaned transaction rows | 530,104 |
| Date range | 2010-12-01 to 2011-12-09 |
| Distinct orders | 19,960 |
| Total revenue | 10,666,684.54 |
| Average order value | 534.40 |
| Countries | 38 |
| Distinct customers with an ID | 4,338 |
| Peak month | November 2011 |
| Peak-month revenue | 1,509,496.33 |
| United Kingdom revenue | 9,025,222.08 |
| United Kingdom distinct orders | 18,019 |
| Top customer | 14646 |
| Top customer revenue | 280,206.02 |
| Top customer distinct orders | 73 |
| Top product SKU | DOT |
| Top product description | DOTCOM POSTAGE |
| Top product units sold | 706 |
| Top product revenue | 206,248.77 |

## Business interpretation

### 1. Revenue is highly concentrated in the United Kingdom
The United Kingdom accounts for 84.61% of verified revenue. A country-level dashboard should make UK performance visible while allowing the user to compare the remaining markets separately.

### 2. November is the strongest observed revenue month
November 2011 generated 1,509,496.33, equal to 14.15% of verified revenue. A monthly trend visual should make this peak easy to inspect alongside order volume.

### 3. A small number of customers can materially affect revenue
Customer 14646 generated 280,206.02, or 2.63% of total verified revenue. Customer-level analysis should therefore include concentration metrics rather than relying only on aggregate revenue.

## Caveats

These are descriptive findings from the cleaned dataset. They do not establish causation, customer lifetime value, profitability, or future demand. Revenue is in the dataset's monetary units, not assumed to be INR. Query fixtures are not proof of a successful live PostgreSQL load.
