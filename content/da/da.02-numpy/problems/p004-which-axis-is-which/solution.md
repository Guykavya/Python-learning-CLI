## Approach

Name the axis that must vanish. A column mean collapses the rows (axis 0); a row maximum collapses the columns (axis 1). For a stack of images both the height and width axes vanish, and reductions accept a **tuple** of axes: `axis=(1, 2)`.

## Code

```python
import numpy as np


def column_means(a):
    return a.mean(axis=0)


def row_maxes(a):
    return a.max(axis=1)


def per_image_mean(stack):
    return stack.mean(axis=(1, 2))
```

## Complexity

Each function reads every element once: O(size of the input), all in compiled code.

## Another way

`stack.reshape(len(stack), -1).mean(axis=1)` flattens each image into one row first (Ch. 5.1) and then averages each row; it gives the same numbers. Tests on square arrays could never tell axis 0 from axis 1, which is why these tests use shapes like `(7, 3)` and `(3, 8)`: always test with non-square data.
