## Approach

This is the skip-collect-report pattern from section 16. The `try` sits inside the loop and wraps
only `float(item)`. The non-finite check is not an exception, so it is a plain `if` after the
conversion. `continue` skips to the next item after recording an error.

## Code

```python
import math


def parse_numbers(items):
    """Return (numbers, errors) for a list of texts."""
    numbers = []
    errors = []
    for n, item in enumerate(items, start=1):
        try:
            value = float(item)
        except ValueError:
            errors.append(f"item {n}: {item!r} is not a number")
            continue
        if not math.isfinite(value):
            errors.append(f"item {n}: {item!r} is not a finite number")
            continue
        numbers.append(value)
    return numbers, errors
```

## Complexity

O(total length of the items).

## Another way

Use `else` on the `try` for the finite check and the append. It is equivalent; `continue` in the
handler keeps the nesting flatter.
