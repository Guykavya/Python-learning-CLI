## Approach

`pd.DataFrame(list_of_dicts, columns=[...])` makes one row per dictionary, fills absent keys with missing values, and puts the columns in the order you list. The raw table has the wrong dtypes (a missing `qty` makes the column `float64`; dates are text). Convert each column once: `to_datetime` for the date, nullable `Int64` for `qty` so that whole numbers stay whole.

## Code

```python
import pandas as pd

COLUMNS = ["order_id", "customer", "order_date", "qty", "price"]


def orders_frame(records):
    df = pd.DataFrame(records, columns=COLUMNS)
    df["order_id"] = df["order_id"].astype("int64")
    df["customer"] = df["customer"].astype("str")
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["qty"] = df["qty"].astype("Int64")
    df["price"] = df["price"].astype("float64")
    return df
```

## Complexity

O(n * c) for n records and c columns.

## Another way

One `astype` with a dictionary: `df.astype({"order_id": "int64", "qty": "Int64", ...})`, then `to_datetime` for the date column. `pd.read_json` on the same data is another route, but it guesses types.
