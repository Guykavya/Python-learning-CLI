# Which matrices are symmetric, diagonal, identity?

Chapter section 2.3. A square matrix can be **identity** (ones on the diagonal, zeros elsewhere), **diagonal** (zeros off the diagonal), **symmetric** (`M == M^T`) or none of these.

```python
import numpy as np


def label(M):
    M = np.array(M)
    if np.array_equal(M, np.eye(len(M))):
        return "identity"
    if np.array_equal(M, np.diag(np.diag(M))):
        return "diagonal"
    if np.array_equal(M, M.T):
        return "symmetric"
    return "general"


mats = [
    [[1, 0], [0, 1]],
    [[2, 0], [0, 3]],
    [[1, 2], [2, 5]],
    [[1, 2], [3, 4]],
]
for M in mats:
    print(label(M))
print(label([[0, 0], [0, 0]]))
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

`label([[4, 0], [0, 4]])` is `diagonal` (not identity: the diagonal is not all ones).

## After you answer

- Is every identity matrix also diagonal and symmetric? Why does the order of the `if`s matter?
