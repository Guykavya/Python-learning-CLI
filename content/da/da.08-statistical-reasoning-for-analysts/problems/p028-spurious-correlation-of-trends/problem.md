# Spurious correlation of trends

Chapter section 7. Two series that both **trend** (or wander, like a random walk) are often strongly correlated even when they
have nothing to do with each other: ice-cream sales and a share price both rising over the years. A standard cure is to correlate
the **changes** (first differences), not the levels.

Write `diff_corr(a, b)`: the Pearson correlation of the first differences `np.diff(a)` and `np.diff(b)`.
Raise `ValueError` (message `r is undefined when one variable does not vary`) when one of the difference series is constant (for
example an exact straight line).

```python
diff_corr([1, 3, 6, 10], [0, 1, 3, 6])     # differences [2, 3, 4] and [1, 2, 3]  ->  1.0
```

## Example

Two independent random walks often have a raw correlation of 0.5 or more in absolute value, while the correlation of their changes
stays near 0.
