## Hint 1

Why can `0.1 + 0.2 == 0.3` be `False`? What would a fair comparison of two floats look like?

## Hint 2

`math.isclose(x, y)` uses a relative tolerance: a tiny difference compared with the size of the numbers.
Compared with zero, any difference is "large" in relative terms, so you also need `abs_tol`.

## Hint 3

`print("Close:", math.isclose(a + b, c, abs_tol=1e-9))`
