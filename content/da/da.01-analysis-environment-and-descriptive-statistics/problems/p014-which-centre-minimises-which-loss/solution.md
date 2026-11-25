## Approach

A tiny optimiser: evaluate the loss at every candidate and take the minimum. The two losses give different winners because squared loss punishes far values heavily (the mean is pulled toward them) while absolute loss counts each unit equally (the median ignores how far the tail goes). Absolute loss is flat between the two middle values of an even list, so the test checks the **loss** of your answer, not the exact point.

## Code

```python
def total_loss(values, c, kind):
    if kind == "squared":
        return sum((x - c) ** 2 for x in values)
    if kind == "absolute":
        return sum(abs(x - c) for x in values)
    raise ValueError(f"unknown loss kind: {kind!r}")

def best_centre(values, kind):
    if not values:
        raise ValueError("empty list")
    mean = sum(values) / len(values)
    candidates = sorted(set(values) | {mean})
    return min(candidates, key=lambda c: total_loss(values, c, kind))
```

## Complexity

O(n * k) with k candidates (up to n + 1), so O(n squared) in the worst case. The closed forms (mean, median) are O(n) and O(n log n).

## Another way

Calculus: the derivative of the squared loss is `-2 * sum(x - c)`, zero when `c` is the mean. For absolute loss the slope is (number below) minus (number above), which changes sign exactly at the median.
