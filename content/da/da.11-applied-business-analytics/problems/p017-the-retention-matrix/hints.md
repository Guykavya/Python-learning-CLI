## Hint 1

You need, for each customer, the order month and the cohort month, and the number of months between them. What is the maximum `k` of a cohort given `asof`? Which cells are above it?

## Hint 2

```text
cohort = first_order.to_period("M"); month = order_date.to_period("M")
k = (month - cohort).apply(attrgetter("n"))  or year*12 + month difference
active = distinct customers per (cohort, k); size = customers per cohort
matrix = active / size; set cells with k > max_k(cohort) to NaN, and fill other missing with 0
```
