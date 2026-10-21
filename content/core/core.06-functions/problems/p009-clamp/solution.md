## Approach

Normalise the input first (swap a reversed range with tuple unpacking), then use guard clauses:
too low returns `low`, too high returns `high`, and anything that survives both checks is
already in range.

## Code

```python
def clamp(value, low=0, high=100):
    """Return value limited to the range low..high (swapping low and high if reversed)."""
    if low > high:
        low, high = high, low
    if value < low:
        return low
    if value > high:
        return high
    return value
```

## Complexity

O(1).

## Another way

After the swap, `return max(low, min(value, high))` does it in one line: `min` caps the value
at `high`, then `max` lifts it to at least `low`. It is compact but takes a moment to verify,
while the guard clauses read like the specification.
