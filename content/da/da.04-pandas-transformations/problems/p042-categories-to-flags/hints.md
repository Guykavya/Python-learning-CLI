## Hint 1

`pd.get_dummies` can encode chosen columns of a frame and keep the rest. Which arguments set the column-name prefix
and make the flags integers instead of `True`/`False` (the default in pandas 3)?

## Hint 2

```text
pd.get_dummies(orders, columns=["channel"], prefix="ch", dtype=int)
```
