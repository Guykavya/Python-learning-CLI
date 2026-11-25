## Approach

- A: 255 / 5100 = 5.00%; B: 294 / 4900 = 6.00%.
- Absolute lift: +1.00 points. Relative lift: 1.0 / 5.0 = +20.0%.
- Expected 5000 per group; chi-square = 100^2 / 5000 + 100^2 / 5000 = 2 + 2 = 4.00, below 10.83: ok.

## Code

```text
A 5.00% | B 6.00%
absolute lift +1.00 points
relative lift +20.0%
SRM chi-square 4.00
SRM verdict: ok
```

## Complexity

Not applicable (a trace problem).

## Another way

The same numbers with `scipy.stats.chisquare([5100, 4900])` give p = 0.0455: a small imbalance, not a mismatch at the strict 0.001 level.
