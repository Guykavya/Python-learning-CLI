# New against repeat customers

Chapter section 15.8 asks how much revenue comes from new and from repeat customers. Here the question is asked **per
month**: in each month, how many customers were new, how many came back, and how much did each group spend?

A customer is **new in the month of their first order**: all their orders in that month count as "new" (a customer who
orders twice in their first month is still new, once). In every later month in which they order, they are a
**repeat** customer.

Write `new_vs_repeat(orders)`:

- `orders` has the columns `order_id`, `customer_id`, `order_date` and `revenue`, in any order (no missing values);
- return a frame with the columns `month` (text `"YYYY-MM"`), `new_customers`, `repeat_customers` (distinct customers,
  integers), `new_revenue`, `repeat_revenue` (sums, floats);
- one row per month that has at least one order, sorted by month, fresh index; a group with nobody in a month shows 0;
- do not change the input.

The tests compare your table with a loop over the customers on random data.

## Example

```python
import pandas as pd

orders = pd.DataFrame({"order_id": [1, 2, 3, 4],
                       "customer_id": ["C1", "C1", "C2", "C1"],
                       "order_date": pd.to_datetime(["2025-01-05", "2025-01-20", "2025-02-03", "2025-02-10"]),
                       "revenue": [100.0, 50.0, 70.0, 30.0]})
print(new_vs_repeat(orders).values.tolist())
```
```text
[['2025-01', 1, 0, 150.0, 0.0], ['2025-02', 1, 1, 70.0, 30.0]]
```
