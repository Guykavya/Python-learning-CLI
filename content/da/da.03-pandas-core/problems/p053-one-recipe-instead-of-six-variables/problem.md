# One recipe instead of six variables

Chapter section 17.1. This script cleans an orders table with a new variable at every step. It works, but nobody can see
the recipe at a glance, and it is easy to use the wrong variable in a later step.

```python
def clean_orders_script(df):
    t1 = df.copy()
    t1["city"] = t1["city"].str.strip().str.title()
    t2 = t1[t1["qty"] > 0]
    t3 = t2.drop_duplicates(subset="order_id", keep="last")
    t4 = t3.assign(revenue=t3["qty"] * t3["unit_price"] * (1 - t3["discount"].fillna(0)))
    t5 = t4[t4["paid"]]
    t6 = t5.sort_values("revenue", ascending=False)
    t7 = t6.reset_index(drop=True)
    return t7[["order_id", "city", "revenue"]]
```

Rewrite it as `clean_orders(df)` whose body is **a single `return` of one method chain** (wrapped in brackets, one step
per line): no temporary variables. The output must be **exactly equal** to the script's output (same rows, same order,
same columns, same dtypes). Use `assign` with `lambda d: ...` for steps that need the frame built so far, and `query`,
`pipe` or `loc` where they read better. The input frame is not changed.

The test checks the shape of your function: its body may contain only a docstring and one `return`.

## Example

```python
import pandas as pd

from solution import clean_orders

df = pd.DataFrame({
    "order_id": [1, 2, 2, 3, 4],
    "city": [" pune", "DELHI ", "delhi", "agra", "surat"],
    "qty": [2, 1, 3, 0, 5],
    "unit_price": [100.0, 50.0, 50.0, 10.0, 20.0],
    "discount": [0.1, None, 0.5, 0.0, None],
    "paid": [True, True, True, True, False],
})
out = clean_orders(df)
print(out["order_id"].tolist(), out["city"].tolist(), out["revenue"].tolist())
print(out.columns.tolist())
```

```text
[1, 2] ['Pune', 'Delhi'] [180.0, 75.0]
['order_id', 'city', 'revenue']
```
