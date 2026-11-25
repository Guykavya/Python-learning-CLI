## Approach

Answer the three questions in order: the cause (NumPy memory layout), the remedy (a mask next to the values) and the timing (convert after you understand the gaps). Compare with `answer.md`, tick the checklist, and rate yourself.

## Code

You can see every claim in the REPL:

```python
import pandas as pd

a = pd.Series([1, None, 3])
b = pd.Series([1, None, 3], dtype="Int64")
print(a.dtype, b.dtype)             # float64 Int64
print((a > 1).tolist())             # [False, False, True]    the gap is silently "not greater"
print((b > 1).tolist())             # [False, <NA>, True]     the gap stays unknown
```

## Complexity

Not applicable: this is an explanation. Memory is about the same (8 bytes per value) plus one byte per value for the mask.

## Another way

You can avoid the problem at read time: `pd.read_csv(path, dtype={"customer_id": "Int64"})` reads the blanks as `<NA>` directly. If an id is only a label (you never add ids), text may be better than any integer type: leading zeros survive and nobody averages them by accident.
