# Duplicates by key

Chapter sections 5.3 and 5.4. Often the real question is not "is the whole row repeated?" but "does the same *thing*
appear twice?": the same respondent, the same order, the same email. A person who fills a form twice gets a new
`resp_id`, so a check on the id alone misses them. Choose the key from the meaning of the data, and say **which copy
survives**: here, the one with the largest value in an ordering column (the newest).

Write `dedupe_by_key(df, key, order_by)`. Return a tuple `(kept, removed)`:

- `key` is a column name; rows with the same value in that column are the same thing (the key has no missing values).
- `order_by` is a column name. For each key, the row with the **largest** `order_by` survives.
- If two rows of the same key share the largest value, the one that comes **later in the table** survives.
- `kept` has one row per key. `removed` has all the other rows (for the change log). Both keep the **original index
  labels and the original row order** (so `kept` is not sorted by `order_by`; it is in the order the table had).
- `kept` and `removed` together contain every row of `df` exactly once. Do not change `df`.

## Example

```python
import pandas as pd

df = pd.DataFrame({
    "email": ["a@x", "b@x", "a@x", "c@x", "b@x", "a@x"],
    "score": [3, 5, 7, 2, 6, 9],
    "sent":  [10, 11, 12, 13, 9, 12],
})
kept, removed = dedupe_by_key(df, "email", "sent")
print(kept.index.tolist(), removed.index.tolist())
print(kept["score"].tolist(), removed["score"].tolist())
```

```text
[1, 3, 5] [0, 2, 4]
[5, 2, 9] [3, 7, 6]
```

For `a@x`, rows 2 and 5 both have `sent` = 12, the largest; the later row (5) wins.
