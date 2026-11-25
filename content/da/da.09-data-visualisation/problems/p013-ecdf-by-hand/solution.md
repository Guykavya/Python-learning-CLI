## Approach

Sorted: `[1, 2, 2, 3, 5]`. The y values are `0.2, 0.4, 0.6, 0.8, 1.0`. A tie produces **two** points at the same x; the drawn step goes from 0.2 straight up to 0.6 at x = 2, so the jump at 2 is `0.6 - 0.2 = 0.4`:
two values (2/5) sit exactly at 2.

## Code

```text
1 0.2
2 0.4
2 0.6
3 0.8
5 1.0
share at or below 2: 0.6
jump at 2: 0.4
```

## Complexity

Not applicable (a trace problem).

## Another way

`np.unique(values, return_counts=True)` with `np.cumsum(counts) / n` gives one point per distinct value (here x = 1, 2, 3, 5 with 0.2, 0.6, 0.8, 1.0), which avoids the repeated x.
