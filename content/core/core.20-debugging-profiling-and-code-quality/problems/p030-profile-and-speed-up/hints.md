## Hint 1

Run the profile from the problem and sort by `tottime`. Look at the `ncalls` column next to
the input sizes: 3,000 orders and 12 months. Which function is called about 3000 × 12 times?
Then read `build_report` and, for each loop, ask "how many times does this inner work run
compared with the number of orders?" There are three places where the answer is "far more
than once per order".

## Hint 2

The three hot spots:

- `find_product` scans the whole product list for every order.
  **Fix:** build a dict `{id: product}` once.
- The `BY MONTH` section re-reads and re-parses (`strptime`) every order once **per month**.
  **Fix:** add each order's amount to its month's total during the main loop.
- The ranking sorts all products again **for every product**, then searches with `index`.
  **Fix:** sort once and number the products with `enumerate`.

## Hint 3

```
products = {pid: {...}}                         # parse once
for each order line (one pass):
    product = products.get(pid); unknown -> skipped += 1; continue
    amount = price * qty
    revenue, per_product[pid], per_month[date[:7]] += amount
BY MONTH:   for month in sorted(per_month): ...
TOP:        order = sorted(per_product, key=lambda p: (-per_product[p], p))
            for rank, pid in enumerate(order, start=1): ...
```

After each fix, compare your output with the original on the fixture files and on a big random
input. A faster wrong answer is worth nothing.
