# `keep="first"`, `"last"`, `False`

Chapter section 5.2. The `keep` argument decides which copies of a repeated key survive. A table has nine rows; the
last two have **no id**. Trace which `row_id`s each option keeps.

```python
import pandas as pd

df = pd.DataFrame({
    "row_id": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    "id": ["a", "b", "a", "c", "b", "a", "d", None, None],
})
for k in ["first", "last", False]:
    kept = df.drop_duplicates(subset="id", keep=k)
    print(k, kept["row_id"].tolist())
print(int(df.duplicated(subset="id").sum()), int(df.duplicated(subset="id", keep=False).sum()))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `u = pd.DataFrame({"row_id": [1, 2, 3], "id": ["x", "y", "x"]})`, `u.drop_duplicates(subset="id", keep="last")["row_id"].tolist()`
is `[2, 3]`: the last `x` is kept, and the rows stay in their original order.

## After you answer

- Which option would you use to *look at* every member of a duplicate group, and which to *remove* the repeats?
- Rows 8 and 9 both have a missing id. Does pandas treat them as the same key or as two unknown people? Was that what
  you expected?
