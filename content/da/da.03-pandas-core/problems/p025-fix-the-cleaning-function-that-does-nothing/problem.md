# Fix the cleaning function that does nothing

Chapter section 9.3. A colleague wrote `clean(df)` to repair an order table, ran it, and says: "It runs, but the table comes
out the same, and sometimes pandas prints a warning." The file `solution.py` already contains this code; fix it.

```python
def clean(df):
    """Negative quantities are entry errors: make them 0. Round every price to 2 decimals."""
    df[df["qty"] < 0]["qty"] = 0
    for i in range(len(df)):
        df["price"][i] = round(df["price"][i], 2)
    return df
```

Required behaviour:

- every negative `qty` becomes `0`; other quantities stay (the dtype stays `int64`);
- every `price` is rounded to 2 decimals; a missing price stays missing;
- the **result is a new frame** and the **input frame is not changed**;
- the index labels (they need not be `0, 1, 2, ...`) and all other columns are kept;
- **no warning** of any kind: the tests run with warnings turned into errors.

## Symptoms the colleague reported

1. "After `clean(df)` there are still negative quantities."
2. "The prices were not rounded either, and there was a `ChainedAssignmentError` message."
3. "The loop is slow on a big table."

## Example

```python
df = pd.DataFrame({"qty": [3, -1, 5], "price": [1.234, 2.5, 3.14159]}, index=[7, 8, 9])
clean(df)["qty"].tolist()       # [3, 0, 5]
clean(df)["price"].tolist()     # [1.23, 2.5, 3.14]
df["qty"].tolist()              # [3, -1, 5]   unchanged
```
