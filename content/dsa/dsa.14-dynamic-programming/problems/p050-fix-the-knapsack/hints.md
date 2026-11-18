## Hint 1

Trace `knapsack([2], [10], 7)`. The loop goes `c = 2, 3, 4, ...`. `best[2] = best[0] + 10 = 10`. Then `best[4] = max(0, best[2] + 10)`. But `best[2]` was set to 10 **in this same pass, by this same parcel**. So `best[4] = 20` uses the parcel twice, and `best[6] = 30` three times.

## Hint 2

The starter is the **unbounded** knapsack (chapter section 11): reading a cell already updated for this parcel means "take it again". For the 0/1 knapsack the cell `best[c - w]` must still hold the value from before this parcel. Smaller indices are updated **later** if the loop goes from high to low.

## Hint 3

Change only the inner loop:

```
for c from capacity down to weights[i]:
    best[c] = max(best[c], best[c - weights[i]] + values[i])
```

In Python: `range(capacity, weights[i] - 1, -1)`. Mind the `- 1`: the loop must still include `c == weights[i]`.
