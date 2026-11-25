# Wald against Wilson

Chapter section 13.6. An interval for a proportion from `k` successes out of `n`. The **Wald** interval `p +- z sqrt(p (1 - p) / n)` collapses when `k = 0`. The **Wilson** interval does not.

```python
import math


def wald(k, n, z=1.96):
    p = k / n
    se = math.sqrt(p * (1 - p) / n)
    return max(0.0, p - z * se), min(1.0, p + z * se)


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, centre - half), min(1.0, centre + half)


for name, f in [("Wald", wald), ("Wilson", wilson)]:
    lo, hi = f(0, 20)
    print(f"{name}: ({lo:.3f}, {hi:.3f}) width {hi - lo:.3f}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For `k = 10, n = 20` the Wald interval would be `(0.281, 0.719)`.

## After you answer

- Zero successes in 20 trials: is it believable that the true rate is exactly 0? Which interval says what?
