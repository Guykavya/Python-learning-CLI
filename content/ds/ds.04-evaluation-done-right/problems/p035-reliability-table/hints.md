## Hint 1

Compute the bin number of every row first (one NumPy expression). Then group by it.

## Hint 2

```text
k = minimum(floor(p * bins), bins - 1)
table = DataFrame({"k": k, "y": y, "p": p}).groupby("k").agg(n=("y", "size"), predicted=("p", "mean"), observed=("y", "mean"))
table["bin_low"] = table.index / bins
```
