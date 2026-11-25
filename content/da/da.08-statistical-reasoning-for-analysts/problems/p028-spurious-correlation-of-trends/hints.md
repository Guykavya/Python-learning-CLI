## Hint 1

What are the "changes" of a series in NumPy, and which function gives a correlation between two arrays? What happens when one array has no spread?

## Hint 2

```text
da, db = np.diff(a), np.diff(b)
if da.std() == 0 or db.std() == 0: raise ValueError(...)
return np.corrcoef(da, db)[0, 1]
```
