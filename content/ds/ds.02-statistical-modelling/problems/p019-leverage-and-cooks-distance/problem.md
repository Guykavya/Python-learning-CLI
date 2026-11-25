# Leverage and Cook's distance

Chapter section 9.3. A point can be unusual in `x` (high **leverage**), unusual in `y` (a large residual), or both. **Cook's distance** measures how much the whole fit would change if the row were deleted. A common rule of thumb flags rows with `D > 4/n`.

Write `influential_points(result, threshold=None)`. It takes a fitted OLS results object and returns a **list of row positions** (integers, starting at 0) whose Cook's distance is **strictly greater** than the threshold (default `4/n`), **sorted from the largest Cook's distance to the smallest**. If nothing is flagged, return `[]`.

## Example

```text
50 well-behaved points plus one point at (x = 6, y = -10), position 50:
influential_points(res)   ->  [50, ...]      # the planted point first
```
