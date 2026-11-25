# A full calendar

Chapter sections 9.1 and 9.2. Grouping orders by date gives one row per day **with sales**; days without an order are
simply absent. A chart or a rolling average then quietly skips them. The shop is open every day, so a day without an
order is a day with **zero** revenue.

Write `daily_sales(orders, start, end)`:

- `orders` has the columns `order_id`, `order_date` (dates without a time) and `revenue`; several orders can share a
  day, and some orders fall outside the period;
- `start` and `end` are date texts such as `"2025-03-01"`; both days are included;
- return a frame with the columns `date` and `revenue`: exactly one row per calendar day from `start` to `end`, in
  order, with the total revenue of that day and `0.0` for a day without orders; orders outside the period are ignored;
- do not change the input.

## Example

```python
import pandas as pd

orders = pd.DataFrame({"order_id": [1, 2, 3],
                       "order_date": pd.to_datetime(["2025-03-01", "2025-03-01", "2025-03-03"]),
                       "revenue": [100.0, 50.0, 20.0]})
out = daily_sales(orders, "2025-03-01", "2025-03-04")
print(out["date"].dt.strftime("%m-%d").tolist(), out["revenue"].tolist())
```
```text
['03-01', '03-02', '03-03', '03-04'] [150.0, 0.0, 20.0, 0.0]
```
