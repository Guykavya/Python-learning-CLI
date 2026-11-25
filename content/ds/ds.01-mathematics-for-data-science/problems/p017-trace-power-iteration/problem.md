# Trace power iteration

Chapter section 4.3. Three steps of the power method on a small matrix, starting from `[1, 0]`.

```python
import numpy as np

A = np.array([[2.0, 1.0], [1.0, 2.0]])
v = np.array([1.0, 0.0])
for step in range(1, 4):
    w = A @ v
    v = w / np.linalg.norm(w)
    print(f"step {step}: {v[0]:.3f} {v[1]:.3f}")
print(f"{v @ A @ v:.3f}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For `A = [[1, 0], [0, 1]]` and `v = [1, 0]` the first step would print `step 1: 1.000 0.000`.

## After you answer

- Which vector are the numbers approaching, and what is the eigenvalue?
