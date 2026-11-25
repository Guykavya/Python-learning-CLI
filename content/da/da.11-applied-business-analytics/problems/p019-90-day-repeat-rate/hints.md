## Hint 1

Two steps: select the eligible customers by their first order date, then, among them, find who has a second order and when. How do you get the second order date of each customer?

## Hint 2

```text
cut = asof - Timedelta(days=90); eligible = customers[first_order <= cut]
o = orders sorted by date; second = o.groupby(customer_id).nth(1) -> order_date per customer
days = second - first_order; repeaters = eligible with days <= 90
```
