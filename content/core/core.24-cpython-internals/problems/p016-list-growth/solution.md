## Approach

`sys.getsizeof(lst)` is the list header plus one pointer per **allocated** slot. It changes
exactly when `append` replaces the slot block, so recording the length whenever the size differs
from the previous size gives the growth points. The model cost is the number of existing items
at each growth point. Subtracting the empty list's size and dividing by the pointer size turns
bytes into slots.

## Code

```python
import struct
import sys


def growth_points(n):
    lst = []
    previous = sys.getsizeof(lst)
    points = []
    for _ in range(n):
        lst.append(None)
        size = sys.getsizeof(lst)
        if size != previous:
            points.append(len(lst))
            previous = size
    return points


def copy_cost(n):
    return sum(p - 1 for p in growth_points(n))


def capacity(lst):
    return (sys.getsizeof(lst) - sys.getsizeof([])) // struct.calcsize("P")
```

On Python 3.14 (64-bit) `growth_points(100_000)` has 66 points and `copy_cost(n) / n` is about
8. The new size is computed as roughly `n + n // 8 + 6`, so the block grows by about 12.5%
each time. The total copying is then a geometric series, about `n / 0.125 = 8n` in this model:
a constant per append. (In reality `realloc` can sometimes grow the block in place and copy
nothing, so the model is an upper bound.)

## Complexity

`growth_points(n)` and `copy_cost(n)` are O(n) time and O(n) memory. `capacity` is O(1).

## Another way

Watch the capacity instead of the raw size:

```python
def growth_points(n):
    lst, points, cap = [], [], 0
    for _ in range(n):
        lst.append(None)
        if capacity(lst) != cap:
            cap = capacity(lst)
            points.append(len(lst))
    return points
```

This shows the meaning better: a growth point is where the capacity jumps.
To see why over-allocation matters, compare with an array that grows by exactly one slot: its
growth points would be `1, 2, 3, ..., n` and its copy cost `n(n-1)/2`, which is 5 billion
copies for 100,000 appends instead of under a million.
