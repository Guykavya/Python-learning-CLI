## Hint 1

For `mean_latency`, list what a hit costs and what a miss costs. Then the average is "fraction of hits x cost of a hit + fraction of misses x cost of a miss". Does the lookup cost disappear on a miss?

## Hint 2

```text
hit costs:  lookup
miss costs: lookup + db
mean = ratio * lookup + (1 - ratio) * (lookup + db) = lookup + (1 - ratio) * db

break-even: lookup + (1 - r) * db == db
            lookup == r * db
            r == lookup / db          (only if lookup < db; otherwise None)
```
