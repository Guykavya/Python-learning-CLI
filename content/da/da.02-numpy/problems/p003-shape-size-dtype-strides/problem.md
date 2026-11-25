# Shape, size, dtype, strides

Chapter sections 3.1 to 3.3 and 5.3. Every array is a block of memory plus a recipe for reading it: the **shape**
and the **strides** (how many bytes to jump to move one step along each axis). All arrays here are `int64`, so one
element is 8 bytes.

```python
import numpy as np

a = np.arange(6, dtype=np.int64).reshape(2, 3)
t = a.T
c = np.arange(24, dtype=np.int64).reshape(2, 3, 4)
s = a[:, ::2]

for name, x in [("a", a), ("t", t), ("c", c), ("s", s)]:
    print(name, x.shape, x.ndim, x.size, x.strides)
print(s.tolist())
print(t.tolist())
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `np.arange(12, dtype=np.int64).reshape(3, 4)` the line would be `m (3, 4) 2 12 (32, 8)`: one row is 4 elements of
8 bytes, so moving down a row jumps 32 bytes.

## After you answer

- `t` and `s` were made without copying anything. How do their strides show that?
- Why is the stride along the columns of `s` 16 and not 8?
