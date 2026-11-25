# Overflow and promotion

Chapter sections 4.2 and 4.5. A `uint8` holds 0 to 255. What happens when you add numbers to it depends on **what**
you add: a Python number (a "weak" scalar), a NumPy scalar (a "strong" one), or a float. One of the five lines below
raises an exception; the program catches it and prints only its class name.

```python
import numpy as np

px = np.array([200, 250], dtype=np.uint8)

r1 = px + 100
print(r1.tolist(), str(r1.dtype))

try:
    r2 = px + 300
    print(r2.tolist(), str(r2.dtype))
except Exception as exc:
    print(type(exc).__name__)

r3 = px + np.int64(100)
print(r3.tolist(), str(r3.dtype))

r4 = px + 2.5
print(r4.tolist(), str(r4.dtype))

f = np.array([1.0, 2.0], dtype=np.float32)
r5 = f + 1.5
print(r5.tolist(), str(r5.dtype))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. The rules are those of
NumPy 2 (the version this course uses).

Do not run the code before you have written your answer.

## Example

`np.array([10], dtype=np.uint8) + 5` prints, with the same `print` as above, `[15] uint8`: the Python `5` adapts to
`uint8`.

## After you answer

- Which line would you get wrong in a real image filter without noticing, and why does NumPy not warn there?
- Why does `r3` not wrap round although `r1` does?
