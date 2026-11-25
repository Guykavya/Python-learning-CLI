## Hint 1

`pd.crosstab(rows, columns)` counts pairs from two Series. Which `normalize=` value makes each **row** add up to 1
("of each region's orders")?

## Hint 2

```text
counts = pd.crosstab(orders["region"], orders["channel"])
shares = pd.crosstab(orders["region"], orders["channel"], normalize="index")
return counts, shares
```
