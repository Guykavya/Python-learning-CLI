# Replace `iterrows`

Chapter sections 15.1 and 15.3. This loop computes the total of every order line with a **tiered discount**: 10% off
when `qty` is 10 or more, 5% off when `qty` is 5 to 9, no discount below 5.

```python
def line_totals_loop(df):
    totals = []
    for _, row in df.iterrows():
        if row["qty"] >= 10:
            discount = 0.10
        elif row["qty"] >= 5:
            discount = 0.05
        else:
            discount = 0.0
        totals.append(row["qty"] * row["unit_price"] * (1 - discount))
    return pd.Series(totals, index=df.index, name="total")
```

It is correct but slow. Write `line_totals(df)` that returns **the same Series** (same values, same index, name `"total"`)
**without any Python loop, `iterrows`, `apply` or list comprehension over rows**. The test also times your function on
200,000 rows and compares it with the `iterrows` loop above, measured on the same machine: yours must be at least
10 times faster. The input frame is not changed.

## Example

```python
import pandas as pd

from solution import line_totals

df = pd.DataFrame({"qty": [1, 5, 9, 10, 20], "unit_price": [100.0, 100.0, 10.0, 10.0, 1.0]}, index=list("abcde"))
out = line_totals(df)
print(out.name, out.index.tolist())
print(out.tolist())
```

```text
total ['a', 'b', 'c', 'd', 'e']
[100.0, 475.0, 85.5, 90.0, 18.0]
```
