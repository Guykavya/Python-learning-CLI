## Hint 1

What does `np.arange(h)` give you, and how could each of those row numbers be repeated across `w` columns? Section 2.3 has a function that builds two coordinate grids at once: which argument decides the number of columns?

## Hint 2

```text
xs, ys = np.meshgrid(np.arange(w), np.arange(h))   # note the order: x first, y second
return ys, xs
```
Or with broadcasting (Ch. 11): `ys = np.arange(h)[:, None] + 0 * np.arange(w)` and the same idea for `xs`.
