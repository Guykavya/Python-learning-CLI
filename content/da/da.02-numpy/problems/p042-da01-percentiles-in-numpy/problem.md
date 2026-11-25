# da.01 percentiles in NumPy

Chapter section 14.2. In da.01 you wrote three percentile definitions by hand (da.01 problem p021):

- **nearest rank**: sort; rank = `max(1, ceil(p * n / 100))` (1-based); the value at that rank. Always a data value.
- **inclusive**: position `(n - 1) * p / 100` (0-based), linear interpolation. Same as `statistics.quantiles(..., method="inclusive")`.
- **exclusive**: position `(n + 1) * p / 100` (1-based), linear interpolation; a position below 1 or above `n` is too extreme and raises `ValueError`. Same as `statistics.quantiles(...)` (default method) where it is defined.

Write `percentile(x, p, method="inclusive")` with `method` one of `"inclusive"`, `"exclusive"`, `"nearest_rank"`, using `np.percentile(..., method=...)` for the calculation. Your job is to find which NumPy method name matches each da.01 definition (Ch. 14.2 names two of them; for nearest rank, read the list of methods in `help(np.percentile)` and test your guess against the definition above).

- Return a Python `float`.
- Raise `ValueError` if `x` is empty, if `p` is outside `[0, 100]`, if `method` is not one of the three names (the message names the bad method), and for `"exclusive"` when the position `(n + 1) * p / 100` is below 1 or above `n` (NumPy itself would quietly clamp it).
- Do not change the caller's data.

## Example

```python
data = [15, 20, 35, 40, 50]
percentile(data, 25)                  # 20.0
percentile(data, 25, "exclusive")     # 17.5
percentile(data, 25, "nearest_rank")  # 20.0
percentile(data, 10, "exclusive")     # ValueError: position 0.6 is outside 1..5 for the exclusive method
```
