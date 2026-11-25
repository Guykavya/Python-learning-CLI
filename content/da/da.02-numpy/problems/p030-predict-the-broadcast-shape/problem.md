# Predict the broadcast shape

Chapter section 11.2 (the two rules). This is the module's learning outcome "predict the shape of a broadcast result": no NumPy at the desk, only the rules.

1. Line the two shapes up on the **right**; pad the shorter one with `1`s on the left.
2. On every axis the two lengths must be **equal**, or one of them must be **1** (it is stretched). Otherwise: error.
3. The result has the larger length on every axis.

```python
import numpy as np

pairs = [
    ((3, 1), (4,)),
    ((5, 1, 4), (3, 1)),
    ((2, 3), (3, 2)),
    ((8, 1, 6, 1), (7, 1, 5)),
    ((4, 3), (4,)),
    ((6,), (6, 1)),
    ((2, 1, 3), (4, 3)),
    ((3, 4), (3, 4, 1)),
]
for a_shape, b_shape in pairs:
    a = np.zeros(a_shape)
    b = np.ones(b_shape)
    try:
        result = a + b
        print(a_shape, "+", b_shape, "->", result.shape)
    except ValueError:
        print(a_shape, "+", b_shape, "-> error")
```

Hand-trace the program and write **every line it prints** in `answer.txt` (eight lines). A shape prints as a Python tuple, so a one-axis shape keeps its comma: `(4,)`.

Do not run the code before you have written your answer.

## Example

For the pair `((3, 4), (4,))` the program would print:

```text
(3, 4) + (4,) -> (3, 4)
```

because `(4,)` is padded to `(1, 4)`; axis 1 is 4 vs 4 (equal), axis 0 is 3 vs 1 (stretch).

## After you answer

- For each `error` line, name the axis where the rule fails.
- `(6,) + (6, 1)` does not give `(6,)`. What did you get, and why is this a common bug when a column vector meets a 1-D array?
