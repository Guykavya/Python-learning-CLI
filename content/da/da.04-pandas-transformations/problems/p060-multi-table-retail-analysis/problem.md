# Multi-table retail analysis

**The project of the chapter (section 15).** The owner of the shop gives you the six tables and wants answers. Every
number must be **traceable**: every join keeps its row count, every breakdown adds up to the total, and the unknowns
(orphan orders, unsold products, customers who never ordered) are shown, not hidden.

Write `analyse(tables)`. `tables` is a dict with the chapter's six tables and column names:

| key | columns |
|---|---|
| `customers` | `customer_id`, `city`, `segment`, `signup` |
| `products` | `product_id`, `category`, `list_price` |
| `stores` | `store_id`, `store_city`, `region` |
| `orders` | `order_id`, `customer_id`, `store_id`, `order_date`, `channel` |
| `items` | `order_id`, `product_id`, `qty`, `unit_price` |
| `returns` | `order_id`, `product_id`, `reason`, `refund` (the refunded share of the line: 0.5 or 1.0) |

Some orders have a `customer_id` that is not in `customers` (orphans): keep them. Put your own `safe_merge` (problem
p057) and `reconcile` (p058) into `solution.py` and use them. Nothing is imported from a course module.

## Rules

1. The working table has the grain **one row per order line**. `revenue = qty * unit_price`. Join the lines to
   `orders`, `products` and `stores` (`validate="m:1"`) and to `returns` on `order_id` + `product_id`
   (`validate="1:1"`), each with `safe_merge`, `measure="revenue"`, and one shared `ledger` list. A duplicated product
   or store row must make `analyse` fail (`MergeError` or `AssertionError`).
2. Reconcile at least three breakdowns with `reconcile` and keep a list `checks` of `(label, ok)` pairs. If a check
   fails, raise `ValueError`.

## What `analyse` returns

A dict with exactly these keys:

| key | value |
|---|---|
| `"total_revenue"` | total revenue of all lines (`float`) |
| `"by_region_channel"` | frame `region, channel, revenue, orders` (distinct orders), sorted by region and channel, fresh index |
| `"top_products"` | frame `category, product_id, revenue, rank`: the 3 best products per category by revenue (ties: smaller `product_id` first), `rank` 1, 2, 3 (an integer), sorted by category and rank, fresh index; categories with fewer sold products have fewer rows |
| `"unsold"` | sorted list of `product_id`s that never appear in `items` |
| `"never_ordered"` | sorted list of `customer_id`s of `customers` with no order |
| `"net_revenue"` | `sum(revenue * (1 - refund))`, refund 0 for lines without a return (`float`) |
| `"return_rate"` | returned lines / all lines (`float`) |
| `"monthly"` | frame `month` (text `"YYYY-MM"`), `revenue`, `mom_pct` (`pct_change() * 100`; the first is `NaN`), sorted, fresh index. If a month between the first and the last has **no** order, `pct_change` would compare the wrong months: raise `ValueError` naming the missing month(s) instead |
| `"ledger"` | the list of `safe_merge` records |
| `"checks"` | the list of `(label, ok)` pairs from `reconcile` |

Do not change the input tables. The tests compare every answer with their own plain-Python loops, on the small data set
below and on six random ones.

## Example

The test data (`conftest.py`) has 10 orders and 15 lines in January to March 2025, one orphan order (customer `C9`),
two unsold products and two customers who never ordered. A correct solution gives:

```text
total_revenue 1670.0   net_revenue 1360.0   return_rate 0.2
unsold ['P6', 'P7']   never_ordered ['C5', 'C6']
by_region_channel revenue [560.0, 665.0, 135.0, 310.0]   (north/online, north/store, west/online, west/store)
top_products grocery: P4 380.0, P1 345.0, P2 190.0   (P3 also has 190.0: the tie goes to P2)
monthly revenue [370.0, 360.0, 940.0]
```

## After you finish

- Which of the answers would change if the orphan order were dropped by an inner join, and which check would catch it?
- Why is `orders` in `by_region_channel` safe to add up across rows, but not if you grouped by `category`?
