## Approach

Python's `and`, `or`, `not` do not work on Series (they ask for one True/False). Use `&`, `|`, `~` instead, which work element by element. Because `&` and `|` bind **tighter** than `>=` and `==`, every comparison needs its own parentheses, and the `or` part needs parentheses too so that the cancelled filter applies to both branches. Building the pieces as named masks keeps each line short.

## Code

```python
import pandas as pd


def big_orders(df, city, min_amount):
    local_big = (df["city"] == city) & (df["amount"] >= min_amount)
    keep = (local_big | df["rush"]) & ~(df["status"] == "cancelled")
    return df[keep]
```

## Complexity

O(n) for building the masks and filtering.

## Another way

`df["status"].ne("cancelled")` instead of `~(... == ...)`, or `df.query("status != 'cancelled' and (...)")` (section 8.4). `query` allows `and`/`or` words.

## Note

`df["city"] == city & df["amount"] >= min_amount` is read as `df["city"] == (city & df["amount"]) >= min_amount`: `&` runs first, and a text value cannot be combined with `&` (a `TypeError`; with two Series it would be the ambiguous-truth `ValueError`). Parenthesise every comparison.
