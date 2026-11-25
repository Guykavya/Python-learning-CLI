# Predict alignment

Chapter sections 2.4 and 4.3. Two Series with different labels: arithmetic matches **labels**, not positions.

```python
import pandas as pd

a = pd.Series([1, 2, 3], index=["a", "b", "c"])
b = pd.Series([10, 20, 30], index=["b", "c", "d"])

total = a + b
print(total.index.tolist())
print(total.tolist())
print(str(total.dtype))
print(a.add(b, fill_value=0).tolist())
print((a.values + b.values).tolist())
print(type(a.values).__name__)
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `x = pd.Series([1, 2], index=["p", "q"])` and `y = pd.Series([5, 6], index=["q", "r"])`, `(x + y).tolist()` prints
`[nan, 7.0, nan]`: labels `p, q, r`, and only `q` is in both.

## After you answer

- Why is the dtype of `total` not `int64` although both inputs are integers?
- Which of the two sums is the one you would trust for "units sold per product"? Which one silently ignores the labels?
