## Approach

The shape is: split on commas, split each piece on a dash, validate, expand, collect in a set, sort. The validation order matters: first the shape (at most two bounds, each a whole number), then the meaning (low not above high). Raising `ValueError` with a **specific** word in the message is what lets the tests (and later the user) tell the two kinds of mistake apart.

## Code

```python
def parse_ranges(text):
    if text.strip() == "":
        return []
    numbers = set()
    for piece in text.split(","):
        piece = piece.strip()
        bounds = [b.strip() for b in piece.split("-")]
        if len(bounds) > 2:
            raise ValueError(f"invalid piece {piece!r}")
        for b in bounds:
            if not b.isdigit():
                raise ValueError(f"invalid piece {piece!r}")
        low = int(bounds[0])
        high = int(bounds[-1])
        if low > high:
            raise ValueError(f"reversed range {piece!r}")
        for n in range(low, high + 1):
            numbers.add(n)
    return sorted(numbers)
```

## Complexity

O(k log k) for k resulting numbers (sorting), plus the size of the text.

## Another way

Keep a list and build `sorted(set(result))` at the end. For huge ranges (`"1-1000000"`) a set of range objects and merging would use less memory: a good follow-up exercise.
