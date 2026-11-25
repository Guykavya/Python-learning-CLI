## Hint 1

For each rule ask: what does the pandas default do with the same data? (`Series.sum` skips `NaN`; `round` uses a different rounding rule; `==` is case-sensitive.)

## Hint 2

Rule 2: with `[10, 5, None, 3.5]` the Excel average divides by the three numbers (6.17); pandas also skips NaN, but if the blank had been read as 0 (a common import choice) the average would be 4.63. Rule 3: `round(2.5)` in Python is 2.
