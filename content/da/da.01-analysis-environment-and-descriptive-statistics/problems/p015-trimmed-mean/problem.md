# Trimmed mean

Chapter section 9.1. A **trimmed mean** sorts the data, throws away the lowest and highest few values, and averages the rest: a compromise between the mean (fragile) and the median (very robust).

Write `trimmed_mean(values, proportion=0.1)`:

- `k = floor(n * proportion)` values are cut from **each** end (so `2 * k` in all);
- the result is the mean of what remains;
- `proportion = 0` is the ordinary mean;
- `proportion` below 0 or **0.5 or more** raises `ValueError` (nothing would be left); an empty list also raises `ValueError`;
- the caller's list must **not** be changed (no `values.sort()`).

## Example

```python
trimmed_mean([1, 2, 3, 4, 100], 0.2)   # n = 5, k = 1: mean of [2, 3, 4] = 3.0
trimmed_mean([1, 2, 3, 4, 100], 0)     # 22.0
```
