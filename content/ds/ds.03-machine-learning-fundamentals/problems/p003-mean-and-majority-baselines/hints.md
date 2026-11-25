## Hint 1

For classification, how do you count how often each value occurs? What does `np.unique(..., return_counts=True)` return, and in which order are the values?

## Hint 2

```text
if task == "regression": return full(n, mean(y))
if task == "classification":
    values, counts = unique(y, return_counts=True)     # values sorted ascending
    return full(n, values[argmax(counts)])             # argmax returns the first maximum = the smaller value
else: raise ValueError
```
