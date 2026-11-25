## Approach

Each oddity of the file has its own argument. `sep=";"` splits the fields. `decimal=","` and `thousands="."` make `1.250,50` the number 1250.5. `na_values=["-"]` marks the dash as missing, which also lets `qty` be numeric (as `float64`, because of the gap). `parse_dates=["date"]` with `date_format="%d.%m.%Y"` states the day-first format explicitly instead of letting pandas guess (a guess on `05.03.2024` is a classic bug).

## Code

```python
import pandas as pd


def read_shop_csv(path):
    return pd.read_csv(
        path,
        sep=";",
        decimal=",",
        thousands=".",
        na_values=["-"],
        parse_dates=["date"],
        date_format="%d.%m.%Y",
    )
```

## Complexity

O(size of the file): one pass.

## Another way

Read everything as text (`dtype="str"`) and convert each column yourself with `to_numeric` and `to_datetime` (Ch. 18): more code, but every failed conversion can be counted. For a one-off clean file the arguments are shorter.
