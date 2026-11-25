## Hint 1

What does `merge(..., validate="m:1")` do when the right side has a repeated key? Which exception class is it, and how
do you catch exactly that one? Inside the `except` block, which Series method marks the repeated values of
`products["product_id"]`?

## Hint 2

```text
try:
    return lines.merge(products[...], on="product_id", how="left", validate="m:1")
except pd.errors.MergeError as err:
    ids  = products["product_id"]
    dups = sorted(ids[ids.duplicated()].unique())
    raise ValueError(f"duplicated product_id in products: {dups}") from err
```
