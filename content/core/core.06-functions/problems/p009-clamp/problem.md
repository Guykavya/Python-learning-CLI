# Clamp a value into a range

Write `clamp(value, low=0, high=100)` that forces `value` into the range `low..high`:

- below `low`, return `low`;
- above `high`, return `high`;
- otherwise return `value` unchanged.

If the caller passes `low` greater than `high`, the range makes no sense: **swap them** first,
so `clamp(5, 10, 1)` behaves like `clamp(5, 1, 10)`.

**Examples**

```python
clamp(150)                 # 100
clamp(-20)                 # 0
clamp(42)                  # 42
clamp(7, high=5)           # 5
clamp(0.25, low=0.5, high=1.0)  # 0.5
clamp(5, 10, 1)            # 5   (range swapped to 1..10)
clamp(50, low=60)          # 60  (60..100)
```

Use it to see why keyword arguments matter: `clamp(7, high=5)` is clear, `clamp(7, 0, 5)` less so.
