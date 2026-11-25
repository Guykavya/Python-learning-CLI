# View or copy?

Chapter sections 6.1 and 6.2. Slicing and `reshape` give **views** (writes go to the original); fancy indexing and
boolean masks give **copies** (writes do not). But a mask or a fancy index on the **left** of `=` writes into the
original. Follow one array through all of them.

```python
import numpy as np

a = np.arange(6)

s = a[1:4]
s[0] = 100
print(a.tolist())

f = a[[0, 2]]
f[0] = -1
print(a.tolist())

r = a.reshape(2, 3)
r[1, 0] = 30
print(a.tolist())

m = a[a > 4]
m[:] = 0
print(a.tolist())

a[a > 4] = 7
print(a.tolist())

print(s.tolist())
print(r.tolist())
print(f.tolist(), m.tolist())
print(np.shares_memory(a, f), np.shares_memory(a, r))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

```python
b = np.arange(4)
b[::2][0] = 9
print(b.tolist())   # [9, 1, 2, 3]: b[::2] is a view, the write reaches b
```

## After you answer

- `m = a[a > 4]` and `a[a > 4] = 7` both use the same mask. Why does only one of them change `a`?
- At the end, `s` and `r` show values you never wrote into them. Where did those values come from?
