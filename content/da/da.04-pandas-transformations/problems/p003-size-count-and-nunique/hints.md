## Hint 1

For customer C (5 rows: one with a missing product, three without a coupon), work out each count by hand. Which of
`size`, `count`, `nunique` gives 5, which gives 2 for the coupons, and which gives 4 for the products?

## Hint 2

```text
lines.groupby("customer_id", as_index=False).agg(
    lines             = (any column, "size"),
    with_coupon       = ("coupon", "count"),
    distinct_products = ("product_id", "nunique"),
)
```
