## Approach

### 1. Measure and profile the original

On a year of generated data (500 products, 3,000 orders over 12 months) the original takes
about **0.42 s** (machine-specific). The profile (real run, Python 3.14, sorted by `tottime`;
seconds are machine-specific, call counts are not):

```text
         1362282 function calls (1362053 primitive calls) in 1.014 seconds

   Ordered by: internal time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    39000    0.291    0.000    0.544    0.000 _strptime.py:516(_strptime)
    39038    0.099    0.000    0.099    0.000 {method 'strftime' of 'datetime.date' objects}
     6498    0.078    0.000    0.078    0.000 solution.py:13(find_product)
      516    0.071    0.000    0.107    0.000 {built-in method builtins.sorted}
    39000    0.047    0.000    0.591    0.000 _strptime.py:812(_strptime_datetime_datetime)
        1    0.037    0.037    1.014    1.014 solution.py:28(build_report)
    39000    0.036    0.000    0.644    0.000 {built-in method strptime}
   248004    0.036    0.000    0.036    0.000 solution.py:64(<lambda>)
    39000    0.029    0.000    0.772    0.000 solution.py:20(month_of)
```

Reading it:

- `month_of` / `strptime` run **39,000** times for 3,000 orders: 3,000 in the main loop plus
  12 × 3,000 in the `BY MONTH` section. That is hot spot **2** (repeated parsing), 76% of the
  run (`cumtime` 0.772 of 1.014).
- `find_product`: 6,498 calls, each walking up to 500 products. Hot spot **1** (quadratic lookup).
  Small here; dominant with a big catalogue.
- `sorted` called **516** times and the key lambda **248,004** times: one full sort per ranked
  product. Hot spot **3** (sorting inside a loop). It grows with the square of the number of
  products sold.

### 2. Fix one at a time, checking the output after each

1. **Lookup:** `parse_products` builds `{id: product}`; `products.get(pid)` is O(1).
2. **Months:** add `amount` to `per_month[month]` inside the main loop. And since the date is
   always `YYYY-MM-DD`, `date[:7]` is the month: no `strptime` at all.
3. **Ranking:** one `sorted(...)`, then `enumerate(order, start=1)` gives each rank directly.

### 3. Measure again

Same input, real run: **0.0026 s** instead of 0.42 s, about **160 times faster**
(machine-specific). The profile after:

```text
         13520 function calls in 0.008 seconds

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.004    0.004    0.008    0.008 solution.py:12(build_report)
     9000    0.002    0.000    0.002    0.000 {method 'get' of 'dict' objects}
     3500    0.001    0.000    0.001    0.000 {method 'split' of 'str' objects}
        2    0.000    0.000    0.000    0.000 {built-in method builtins.sorted}
```

All the time is now in the one loop that has to read each order once; there is no hot spot left
worth fixing.

## Code

```python
def parse_products(products_csv):
    products = {}
    for line in products_csv.strip().splitlines()[1:]:
        pid, name, category, price = line.split(",")
        products[pid] = {"id": pid, "name": name, "category": category, "price": int(price)}
    return products


def build_report(products_csv, orders_csv):
    products = parse_products(products_csv)
    count = skipped = revenue = 0
    per_product = {}
    per_month = {}
    for line in orders_csv.strip().splitlines()[1:]:
        _order_id, date, pid, qty = line.split(",")
        product = products.get(pid)
        if product is None:
            skipped += 1
            continue
        count += 1
        amount = product["price"] * int(qty)
        revenue += amount
        per_product[pid] = per_product.get(pid, 0) + amount
        month = date[:7]
        per_month[month] = per_month.get(month, 0) + amount

    lines = ["SALES REPORT", f"orders: {count}", f"skipped: {skipped}", f"revenue: {revenue}", "", "BY MONTH"]
    for month in sorted(per_month):
        lines.append(f"{month}  {per_month[month]}")
    lines += ["", "TOP PRODUCTS"]
    order = sorted(per_product, key=lambda p: (-per_product[p], p))
    for rank, pid in enumerate(order, start=1):
        product = products[pid]
        lines.append(f"{rank:>3}. {pid}  {product['name']} ({product['category']})  {per_product[pid]}")
    return "\n".join(lines) + "\n"
```

## Complexity

With N orders, P products, M months and R products sold:

| Part | Original | Fixed |
|---|---|---|
| product lookup | O(N · P) | O(N) |
| monthly totals | O(M · N) parses | O(N), no parsing |
| ranking | O(R² log R) | O(R log R) |

## Another way

`collections.defaultdict(int)` or `Counter` can replace the `.get(key, 0) + amount` pattern, and
`csv.DictReader` over `io.StringIO(text)` is more robust than `split(",")` if names could ever
contain commas (it is slower, but still one pass). If the dates were not guaranteed to be
`YYYY-MM-DD`, keep one `strptime` per order: still O(N), and still far over the 5x target.
