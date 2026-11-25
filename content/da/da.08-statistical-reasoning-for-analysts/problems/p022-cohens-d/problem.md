# Cohen's d

Chapter section 6.1. A p-value says nothing about the **size** of a difference. **Cohen's d** measures it in units of spread:

`d = (mean(a) - mean(b)) / s_pooled`, with `s_pooled = sqrt(((na - 1) var(a) + (nb - 1) var(b)) / (na + nb - 2))`

where `var` uses `ddof=1`. Rough labels: 0.2 small, 0.5 medium, 0.8 large.

Write `cohens_d(a, b)` for two NumPy arrays or lists, returning a float.

```python
cohens_d([4, 6, 8], [1, 3, 5])        # means 6 and 3, both variances 4, pooled sd 2  ->  1.5
```

## Example

Two groups with the same values give `d = 0`; swapping the groups changes the sign.
