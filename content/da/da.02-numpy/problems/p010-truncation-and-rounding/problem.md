# Truncation and rounding

Chapter section 4.4. Converting floats to integers is where many reports lose a unit. `astype(int)` and `np.round`
follow rules that differ from school arithmetic.

```python
import numpy as np

f = np.array([2.5, 3.5, -1.7, 1e10])
t = f.astype(int)
print(t.tolist(), str(t.dtype))

r = np.round(np.array([0.5, 1.5, 2.5, -0.5]))
print(r.tolist(), str(r.dtype))

print(np.round(f).astype(int).tolist())
print(int(np.floor(-1.7)), int(np.ceil(-1.7)), int(-1.7))
print(float(np.round(2.675, 2)), round(2.675, 2))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. `int` here is the default
integer of NumPy 2, which is `int64`.

Do not run the code before you have written your answer.

## Example

`np.array([1.9, -1.9]).astype(int).tolist()` is `[1, -1]`: the fraction is cut off towards zero.

## After you answer

- Which line would surprise someone who learned "round half up" at school?
- The last line prints two different answers for "2.675 rounded to two places". Which one is "right", and what does that tell you about rounding to decimal places?
