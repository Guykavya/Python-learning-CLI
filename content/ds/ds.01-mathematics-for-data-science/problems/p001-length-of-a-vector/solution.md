## Approach

Square every entry, add them up, take the square root: the Pythagorean theorem in any number of dimensions.

## Code

```python
import math


def norm(v):
    total = 0.0
    for x in v:
        total += float(x) * float(x)
    return math.sqrt(total)
```

## Complexity

O(n) time, O(1) extra space for a vector of n entries.

## Another way

`float(np.sqrt(v @ v))` does the same with one dot product; the loop shows what the dot product hides.
