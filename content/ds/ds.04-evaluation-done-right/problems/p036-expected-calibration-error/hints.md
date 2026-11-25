## Hint 1

Reuse the bin numbers of the reliability table. For each non-empty bin you need three numbers: its size, its mean `p` and its mean `y`.

## Hint 2

```text
k = minimum(floor(p * bins), bins - 1); total = 0
for each bin b with rows: total += abs(mean(y[k == b]) - mean(p[k == b])) * count(k == b)
return total / N
```
