# floor, ceil, trunc and isclose

Four small functions that each use the right tool from `math`, and avoid a classic trap.

1. `floor_ceil_trunc(x) -> tuple[int, int, int]`: return `(math.floor(x), math.ceil(x), math.trunc(x))`.
   (Write it and look at the results for negative numbers: that is the point.)
2. `pages_needed(n_items, per_page) -> int`: how many pages are needed to show `n_items` items with
   `per_page` on each page. It must be **exact for any size of integer**. `per_page <= 0` or
   `n_items < 0` raises `ValueError`.
3. `round_down_to(x, step) -> float`: the largest multiple of `step` that is `<= x`
   (for example a price rounded down to the nearest 0.5). `step <= 0` raises `ValueError`.
4. `close_enough(a, b) -> bool`: `True` if the floats are equal up to floating-point error. Use
   `math.isclose` with `rel_tol=1e-9` **and** `abs_tol=1e-9`.

**Examples**

```python
floor_ceil_trunc(-2.5)        # (-3, -2, -2)
pages_needed(10, 3)           # 4
pages_needed(10**17 + 1, 1)   # 100000000000000001   (exact!)
round_down_to(7.8, 0.5)       # 7.5
round_down_to(-2.3, 1.0)      # -3.0
close_enough(0.1 + 0.2, 0.3)  # True
close_enough(1e-12, 0.0)      # True   (only because of abs_tol)
```
