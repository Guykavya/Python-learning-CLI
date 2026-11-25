## Hint 1

For each interval, check the first test (`lo > 0.5`), then the second (`hi < 0.5`), else the third. Use strict comparisons: equal is not greater.

## Hint 2

```text
(0.60, 1.20): lo 0.60 > 0.5 -> worth it
(0.50, 0.90): lo 0.50 is not > 0.5 ; hi 0.90 not < 0.5 -> inconclusive
(0.10, 0.50): lo not > ; hi 0.50 is not < 0.5 -> inconclusive
(-0.40, 0.30): hi 0.30 < 0.5 -> not worth it
(-1.00, 2.00): straddles -> inconclusive
```
