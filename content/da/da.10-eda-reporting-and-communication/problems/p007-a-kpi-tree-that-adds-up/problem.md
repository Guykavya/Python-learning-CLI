# A KPI tree that adds up

Chapter section 3.3. A KPI tree splits a top number into factors whose **product** gives it back. For an orders table:

```text
revenue = active customers  x  orders per active customer  x  average order value
```

Write `revenue_tree(orders)`. `orders` has one row per order with columns `month` (text such as `"2024-01"`), `customer_id` and `amount`. Return a DataFrame with one row per
month (sorted, index = month) and the columns `active` (distinct customers), `orders_per_active`, `avg_order_value` and `revenue` (sum of amounts).

The three factors multiplied must give the revenue of every month (within rounding error).

## Example

January: customer `a` orders 10 and 20, customer `b` orders 30. Then `active = 2`, `orders_per_active = 1.5`, `avg_order_value = 20`, `revenue = 60 = 2 x 1.5 x 20`.
