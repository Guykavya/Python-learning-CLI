## Approach

`floor(log10(|ref|))` is the power of ten of the uncertainty (1 for 63, 0 for 5.9, -1 for 0.4). Showing one digit beyond it gives about two significant digits of the uncertainty.

## Code

```python
import math


def sig_round(value, ref):
    if ref == 0 or not math.isfinite(ref):
        return f"{value:,.0f}"
    decimals = max(0, 1 - math.floor(math.log10(abs(ref))))
    return f"{round(value, decimals):,.{decimals}f}"
```

## Complexity

O(1).

## Another way

Report "2,578 +- 63" using the same rule for both numbers. In a table keep the same number of decimals within a column.
