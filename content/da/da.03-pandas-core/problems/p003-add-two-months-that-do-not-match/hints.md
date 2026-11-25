## Hint 1

What does `a + b` do with a label found in only one Series? What does the method form `a.add(b, ...)` let you say about that case? And what does a missing value do to an integer column?

## Hint 2

```text
total = a.add(b, fill_value=0)     # missing side counts as 0 (result is float64)
total = total.sort_index()
total = total.astype("int64")      # safe: no NaN is left
```
