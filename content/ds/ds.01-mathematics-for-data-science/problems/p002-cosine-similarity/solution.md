## Approach

Compute the dot product and the two lengths, refuse a zero length, divide.

## Code

```python
import math

import numpy as np


def cosine_similarity(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    nx = math.sqrt(float(x @ x))
    ny = math.sqrt(float(y @ y))
    if nx == 0 or ny == 0:
        raise ValueError("cosine is undefined for a zero vector")
    return float(x @ y) / (nx * ny)
```

## Complexity

O(n) time and O(1) extra space.

## Another way

Normalise both vectors to length 1 first; the cosine is then just their dot product.
