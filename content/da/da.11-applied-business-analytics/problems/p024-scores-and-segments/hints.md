## Hint 1

`qcut` cuts at quantile values; when 80% of the values are 1, several cut points are equal and it raises an error. A rank with `method="first"` gives every customer a distinct number. Which direction does `ascending` have for "higher is better"?

## Hint 2

```text
r = s.rank(method="first", ascending=higher_is_better)
return pd.qcut(r, n, labels=list(range(1, n+1))).astype(int)
segment: write the six rules as if / return in the given order
```
