## Hint 1

Which `read_csv` argument chooses the dtype of a column before the guess is made? Does it take one value for all columns or a mapping from column names? Should `qty` be in it?

## Hint 2

```text
pd.read_csv(path, dtype={"pin": "str", "product_code": "str"})
# qty is not listed: pandas still guesses int64 for it
```
