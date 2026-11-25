# Split into two columns

Chapter section 12.3. A table has one `name` column such as `"Asha Rao"`. Write `split_full_name(df)` that returns a
**new** DataFrame with two extra columns at the end: `first` (the first word) and `last` (everything after the first
word, so `"Meera Iyer Nair"` has first `"Meera"` and last `"Iyer Nair"`).

Rules, stated so the edge cases have one answer:

- Leading and trailing spaces and repeated spaces between the words do not matter.
- A name with **one word** has `last == ""` (an empty string, not missing).
- A **missing** name gives a missing `first` and a missing `last`.
- Use `str.split(n=1, expand=True)`; no loop and no `apply`. Other columns and the index stay as they were, and the input frame is not changed.

Watch the trap: if **no** name in the table has two words, `expand=True` makes only one column.

## Example

```python
import pandas as pd

from solution import split_full_name

df = pd.DataFrame({"id": [1, 2, 3, 4], "name": [" Asha   Rao", "Meera Iyer Nair", "Cher", None]})
out = split_full_name(df)
print(out.columns.tolist())
print(out["first"].tolist())
print(out["last"].tolist())
```

```text
['id', 'name', 'first', 'last']
['Asha', 'Meera', 'Cher', nan]
['Rao', 'Iyer Nair', '', nan]
```
