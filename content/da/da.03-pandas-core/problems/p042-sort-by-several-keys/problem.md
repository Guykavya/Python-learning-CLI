# Sort sellers by several keys

Chapter section 14.2. A table `df` has columns `seller` (text), `revenue` (number, sometimes missing) and `note`
(anything). Write `rank_sellers(df)` that returns the rows in this order:

1. **higher revenue first**;
2. on equal revenue, `seller` **alphabetically** (`"Asha"` before `"Ben"`);
3. rows whose revenue is **missing** come **last** (among themselves ordered by seller name);
4. rows equal on both keys keep their original relative order (a **stable** result).

The rows keep their **original index labels** (do not reset the index), and the input frame is not changed.

## Example

```python
import pandas as pd

from solution import rank_sellers

df = pd.DataFrame({
    "seller": ["Dev", "Asha", "Chitra", "Ben", "Esha"],
    "revenue": [500.0, 500.0, None, 900.0, 500.0],
    "note": ["a", "b", "c", "d", "e"],
})
out = rank_sellers(df)
print(out["seller"].tolist())
print(out.index.tolist())
```

```text
['Ben', 'Asha', 'Dev', 'Esha', 'Chitra']
[3, 1, 0, 4, 2]
```
