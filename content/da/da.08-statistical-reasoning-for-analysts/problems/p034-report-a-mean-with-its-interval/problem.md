# Report a mean with its interval

Chapter section 9.1. A result is a sentence with a number **and** its uncertainty. Write `report_mean(x, label, unit="", level=0.95)`
returning exactly this kind of string:

`Mean monthly spend: 2,578 rupees (95% CI 2,453 to 2,702; n = 500)`

Rules:

- drop `NaN` values first; `n` counts only the real values (with a thousands separator, `f"{n:,}"`);
- the mean and the interval ends come from the t interval of problem 10: `mean +- t(n - 1) * SE`, `SE = s / sqrt(n)` with `ddof=1`;
- the numbers are formatted with `sig_round(value, SE)` of problem 33 (decimals from `SE`; copy your solution into this file);
- `unit` is appended directly after the mean (so pass `" rupees"` with its leading space);
- the level is printed as a whole percent: `int(round(level * 100))`, so `level=0.9` prints `90% CI`;
- raise `ValueError` when fewer than 2 real values remain.

```python
report_mean([10, 12, 14, 16, 18], "Mean weight", " kg")
# 'Mean weight: 14.0 kg (95% CI 10.1 to 17.9; n = 5)'
```

## Example

With `x = [10, 12, nan, 14, 16, 18]` the `nan` is dropped, so `n = 5` and the result is the one above.
