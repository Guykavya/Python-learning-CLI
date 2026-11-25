## Walk-through

`1.3 * 0.30 = 0.39`.

- degree 1: train 0.50 > 0.39: `underfit`
- degree 2: train 0.48 > 0.39: `underfit`
- degree 3: train 0.29 not > 0.39; val 0.31 vs `1.5 * 0.29 = 0.435`: not larger: `good`
- degree 6: train 0.25; val 0.33 vs `1.5 * 0.25 = 0.375`: not larger: `good`
- degree 9: train 0.12; val 0.90 vs 0.18: `overfit`
- degree 12: train 0.05; val 4.10 vs 0.075: `overfit`

Lowest validation error: degree 3 (0.31, versus 0.33 for degree 6).

## Why degree 3

Both are `good`, but degree 3 has the lower validation error and is simpler. A simpler model with the same validation error is preferred (less variance, easier to explain).
