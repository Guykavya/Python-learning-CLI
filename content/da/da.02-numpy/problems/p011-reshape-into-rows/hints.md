## Hint 1

In `reshape(rows, cols)`, which number do you know (the columns) and which one can NumPy work out for you? When can it **not** work it out?

## Hint 2

```text
if k < 1:            raise ValueError(...)
if len(x) % k != 0:  raise ValueError(f"cannot split {len(x)} values into rows of {k}")
return x.reshape(-1, k)
```
