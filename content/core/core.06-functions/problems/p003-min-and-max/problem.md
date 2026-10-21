# Smallest and largest together

Write `min_and_max(numbers)` that returns a **tuple** `(smallest, largest)` for a list of numbers.

For an **empty** list there is no smallest or largest, so return `(None, None)`.

Do not use the built-ins `min` and `max`: walk the list once yourself, keeping the smallest
and largest seen so far. Do not change the list.

**Examples**

```python
min_and_max([4, 9, 1, 7])   # (1, 9)
min_and_max([5])            # (5, 5)
min_and_max([-2, -8])       # (-8, -2)
min_and_max([])             # (None, None)

low, high = min_and_max([3, 1, 2])   # unpack straight into two names
```
