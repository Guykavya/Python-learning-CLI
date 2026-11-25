# Which copy survives?

Chapter section 5.4. When two rows describe the same thing, "keep the newest" is only one survival rule. Another is
**most complete row wins**: keep the copy that has the fewest missing cells, because it carries the most information.
Newer copies are not always better: a short re-submission can lose the phone number the first one had.

Write `best_copy(df, key)`:

- `key` is a column name; rows with the same value in it are copies of the same thing. The key has no missing values.
- `df` has a column `updated_at` (never missing; any values that can be compared: ISO date text, numbers, timestamps).
- For each key, keep **one** row:
  1. the one with the most **non-missing cells** (count over **all** columns of the row, key and `updated_at` included);
  2. on a tie, the one with the **latest** `updated_at`;
  3. if still tied, the one that comes **later in the table**.
- Return the kept rows as a DataFrame, in their **original order, with their original index labels**. Do not change `df`.

## Example

```python
import pandas as pd

df = pd.DataFrame({
    "id": [1, 1, 2, 2, 2, 3],
    "phone": [None, "98", "97", None, "97", None],
    "city": ["Pune", None, "Delhi", "Delhi", "Delhi", None],
    "updated_at": ["2024-01-01", "2024-02-01", "2024-01-10", "2024-03-01", "2024-02-01", "2024-01-01"],
})
print(best_copy(df, "id").index.tolist())
```

```text
[1, 4, 5]
```

For `id` 1 the two copies have 3 filled cells each; the newer one (row 1) wins. For `id` 2, rows 2 and 4 have 4 filled
cells and row 3 only 3, so the newest row 3 loses; of rows 2 and 4 the later `updated_at` is row 4.
