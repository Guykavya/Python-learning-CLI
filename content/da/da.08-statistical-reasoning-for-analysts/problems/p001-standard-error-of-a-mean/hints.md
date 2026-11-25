## Hint 1

Which standard deviation divides by n - 1: the NumPy default or `ddof=1`? And what must happen before you divide when there is only one value?

## Hint 2

```text
x = np.asarray(x, dtype=float)
if len(x) < 2: raise ValueError("one value has no spread")
return x.std(ddof=1) / np.sqrt(len(x))
```
