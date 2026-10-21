## Approach

Apply two limits in a row. `min` acts as a ceiling, `max` acts as a floor.

## Code

```python
value = int(input())
low = int(input())
high = int(input())
print(max(low, min(value, high)))
```

## Why it works

- If `value > high`, `min` gives `high`, and `max(low, high)` is `high`.
- If `value < low`, `min` gives `value`, and `max(low, value)` is `low`.
- Otherwise both functions leave `value` alone.

## Another way

`min(high, max(low, value))` applies the floor first. When `low <= high` it gives the same result.
