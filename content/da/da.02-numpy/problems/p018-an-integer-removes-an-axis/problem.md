# An integer removes an axis

Chapter sections 7.3, 7.4, 5.4 and 9.1. The rule: an **integer** index removes its axis, a **slice** keeps it (even
a slice of length 1), a **list** of positions keeps it with the list's length, `None` **adds** an axis of length 1,
and `...` stands for "all the other axes".

```python
import numpy as np

a = np.zeros((3, 4, 5))
print(a[1].shape)
print(a[1:2].shape)
print(a[:, 1].shape)
print(a[:, [1]].shape)
print(a[..., 0].shape)
print(a[None].shape)
print(a[1, :, 2].shape)
print(a[[0, 2]].shape)
print(a[:, None, :, 0].shape)
print(a[1, 2, 3].shape)
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `b = np.zeros((2, 6))`, `print(b[0].shape)` prints `(6,)` and `print(b[0:1].shape)` prints `(1, 6)`.

## After you answer

- `a[1]` and `a[1:2]` contain the same numbers. When would the extra axis of `a[1:2]` be useful?
- What shape does a single element have, and why?
