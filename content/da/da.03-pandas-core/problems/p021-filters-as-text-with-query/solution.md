## Approach

The text passed to `query` is its own tiny language. Column names are written bare, Python variables get an `@` in front, and a column name that is not a valid identifier (here `unit price`) goes in backticks. Boolean words `and`, `or`, `not` work, so no parentheses are needed around the comparisons. `@region` is a good habit even when a column has the same name: `region == @region` compares the column with the variable.

## Code

```python
import pandas as pd


def query_orders(df, min_qty, region):
    return df.query("qty >= @min_qty and region == @region and `unit price` > 0")
```

## Complexity

O(n), the same work as the mask version.

## Another way

The mask version: `df[(df["qty"] >= min_qty) & (df["region"] == region) & (df["unit price"] > 0)]`. `query` is shorter for long conditions, and is easy to build from user input only if you never paste the values into the text: use `@` variables.
