## Hint 1

Which NumPy functions give you `|a − b|` and `|b|` element by element? A comparison like `x <= y` on arrays gives what kind of array?

## Hint 2

```text
diff = np.abs(a - b)
limit = atol + rtol * np.abs(b)
return diff <= limit           # nan in diff makes the comparison False by itself
```
