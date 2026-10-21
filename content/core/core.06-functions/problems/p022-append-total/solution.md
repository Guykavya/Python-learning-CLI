## Approach

The parameter refers to the caller's list. `append` mutates that object, so the caller sees the
new item. Compute the sum first, then append it. Returning nothing gives `None`, which tells
callers "I changed your object".

## Code

```python
def append_total(numbers):
    """Append sum(numbers) to the end of numbers, in place. Return None."""
    numbers.append(sum(numbers))
```

## Complexity

O(n) for the sum; append is amortised O(1).

## Another way

`numbers += [sum(numbers)]` also mutates in place, because `+=` on a list extends it. The
right-hand side is evaluated before the extension, so the sum is correct.
