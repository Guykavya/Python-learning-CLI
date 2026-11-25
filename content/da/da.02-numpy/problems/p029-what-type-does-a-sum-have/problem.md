# What type does a sum have?

Chapter section 10.6 (`dtype` of an aggregation) and 4 (dtypes). An aggregation does not always keep the dtype of its input: small integer types are summed in a 64-bit accumulator, `mean` of integers is a float, and you can force a narrow accumulator with `dtype=`. Element-wise arithmetic is different: it keeps the narrow type and wraps around.

```python
import numpy as np

flags = np.array([True, False, True, True])
s = flags.sum()
print(int(s), str(s.dtype))

m = np.array([1, 2, 4]).mean()
print(float(m), str(m.dtype))

small = np.array([200, 100], dtype=np.uint8)
total = small.sum()
print(int(total), str(total.dtype))

forced = small.sum(dtype=np.uint8)
print(int(forced), str(forced.dtype))

running = np.cumsum(small)
print(running.tolist(), str(running.dtype))

pair = small + small
print(pair.tolist(), str(pair.dtype))

tiny = np.array([100, 100], dtype=np.int8)
print(int(tiny.sum()), str(tiny.sum().dtype))

f32 = np.array([0.5, 0.25], dtype=np.float32).sum()
print(float(f32), str(f32.dtype))
```

Hand-trace the program and write **every line it prints** in `answer.txt`, one per line. The values are printed with `int()`, `float()` and `.tolist()`, so they look like plain Python numbers; the dtypes are printed with `str(...)`, for example `int64`. (The output is the same on Linux, macOS and Windows with NumPy 2.)

Do not run the code before you have written your answer.

## Example

A line like `print(int(np.array([1, 2], dtype=np.int16).sum()), str(np.array([1, 2], dtype=np.int16).sum().dtype))` prints `3 int64`: a sum of small signed integers is computed in `int64`.

## After you answer

- Which two lines show the uint8 wrap-around, and why does the plain `small.sum()` not wrap?
- If you have a `uint8` image and want its average brightness, is `img.mean()` safe? Is `(img + img) / 2` safe?
