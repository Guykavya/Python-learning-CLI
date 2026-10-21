## Approach

Use tuple assignment. The right side `b, a` is evaluated first and builds a pair of the two
objects. Only then are the names on the left rebound, one by one.

## Code

```python
a = int(input())
b = int(input())
a, b = b, a
print(f"a = {a}")
print(f"b = {b}")
```

## Why it works

Names are labels on objects. `a, b = b, a` first makes the pair `(9, 4)` from the current
objects, then sticks the label `a` on `9` and `b` on `4`. No object is copied or lost.

## Another way

With numbers only, an arithmetic trick also works: `a = a + b`, `b = a - b`, `a = a - b`.
It is harder to read and only works for numbers, so prefer tuple assignment.
