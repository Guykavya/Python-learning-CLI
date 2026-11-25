# Stack or concatenate?

Chapter section 5.5. `concatenate` joins along an **existing** axis; `stack` makes a **new** one. `vstack` and
`hstack` are shortcuts, and `np.column_stack` makes every 1-D input a **column** (2-D inputs are joined side by side,
like `hstack`).

```python
import numpy as np

u = np.array([1, 2, 3])
v = np.array([4, 5, 6])
print(np.concatenate([u, v]).shape)
print(np.stack([u, v]).shape)
print(np.stack([u, v], axis=1).shape)
print(np.vstack([u, v]).shape)
print(np.hstack([u, v]).shape)
print(np.column_stack([u, v]).shape)
print(np.column_stack([u, v]).tolist())

P = np.arange(6).reshape(2, 3)
Q = P + 10
print(np.concatenate([P, Q]).shape)
print(np.concatenate([P, Q], axis=1).shape)
print(np.stack([P, Q]).shape)
print(np.stack([P, Q], axis=1).shape)
print(np.stack([P, Q], axis=2).shape)
print(np.vstack([P, Q]).shape)
print(np.hstack([P, Q]).shape)
print(np.column_stack([P, Q]).shape)
print(np.stack([P, Q], axis=1)[0].tolist())
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

`np.concatenate([np.zeros(2), np.zeros(5)]).shape` prints `(7,)`: a 1-tuple has a comma.

## After you answer

- Which two different calls on `u` and `v` give the same shape `(3, 2)`?
- For the 2×3 arrays, which calls make a 3-D result, and why can `concatenate` never do that?
