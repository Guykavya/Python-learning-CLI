## Approach

Deal with the special case first: an empty list returns `(None, None)` straight away. Otherwise
start both trackers at the first item, which is certainly in the list, then compare every item
against both. `return smallest, largest` builds and returns one tuple.

## Code

```python
def min_and_max(numbers):
    """Return (smallest, largest) of numbers, or (None, None) if it is empty."""
    if not numbers:
        return None, None
    smallest = largest = numbers[0]
    for n in numbers:
        if n < smallest:
            smallest = n
        if n > largest:
            largest = n
    return smallest, largest
```

## Complexity

O(n) time, one pass. O(1) extra space.

## Another way

`return min(numbers), max(numbers)` with the same empty check is the everyday way. It walks the
list twice instead of once, which only matters for huge inputs.
