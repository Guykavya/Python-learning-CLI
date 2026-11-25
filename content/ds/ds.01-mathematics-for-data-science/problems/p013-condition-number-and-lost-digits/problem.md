# Condition number and lost digits

Chapter section 3.6. The chapter builds `make_near_singular(eps)`: a 2 x 2 matrix whose second row is almost a copy of the first (they differ by `eps`).

```python
import numpy as np


def make_near_singular(eps):
    return np.array([[1.0, 1.0], [1.0, 1.0 + eps]])


A = make_near_singular(1e-10)
x_true = np.array([1.0, 2.0])
b = A @ x_true
print(f"{np.linalg.cond(A):.1e}")
print(np.linalg.solve(A, b) - x_true)
```

In `answer.md` explain, in about 200 to 300 words:

1. what the **condition number** says and why `make_near_singular(1e-10)` loses about **10 digits**;
2. the rule of thumb for how many digits you lose;
3. why forming `A^T A` for the normal equations makes things **worse**, and what to use instead.

## Example

A start: "The condition number measures how much a relative error in the input can be amplified in the answer. Here..."
