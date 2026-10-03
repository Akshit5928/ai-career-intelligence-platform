# Verified business insights

Analysis source: UCI Online Retail dataset (UCI dataset ID 352).

## Verified outputs

| Metric | Verified value |
|---|---:|
| Cleaned transaction rows | 530,104 |
| Distinct orders | 19,960 |
| Total revenue | 10,666,684.54 |
| Average order value | 534.40 |
| Countries | 38 |
| Peak month | November 2011 |
| Peak-month revenue | 1,509,496.33 |
| United Kingdom revenue | 9,025,222.08 |
| Top customer | 14646 |
| Top customer revenue | 280,206.02 |

## Business interpretation

### 1. Revenue is highly concentrated in the United Kingdom
The United Kingdom accounts for 84.61% of verified revenue. A country-level dashboard should therefore make UK performance visible while allowing the user to compare the remaining markets separately.

### 2. November is the strongest observed revenue month
November 2011 generated 1,509,496.33, equal to 14.15% of verified revenue. A monthly trend visual should make this peak easy to inspect alongside order volume.

### 3. A small number of customers can materially affect revenue
Customer 14646 generated 280,206.02, or 2.63% of total verified revenue. Customer-level analysis should therefore include concentration metrics rather than relying only on aggregate revenue.

## Caveats
These are descriptive findings from the cleaned dataset. They do not establish causation, customer lifetime value, profitability, or future demand.
