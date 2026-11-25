## Hint 1

Translate the formula line by line: which values do you need first (`z`, `p`), and which two combinations do you build from them?

## Hint 2

```text
z = stats.norm.ppf((1 + level) / 2); p = k / n; d = 1 + z * z / n
centre = (p + z * z / (2 * n)) / d
half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
```
