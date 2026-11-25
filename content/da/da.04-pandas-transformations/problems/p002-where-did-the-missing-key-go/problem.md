# Where did the missing key go?

Chapter section 2.3. By default `groupby` **drops rows whose key is missing**. Nothing warns you: the group totals
simply add up to less than the table. `dropna=False` keeps the missing key as a group of its own.

```python
import pandas as pd

t = pd.DataFrame({
    "store": ["S1", None, "S2", "S1", None, "S3"],
    "sales": [10, 5, 20, 30, 7, 1],
})
a = t.groupby("store")["sales"].sum()
print(a.to_dict())
print(int(a.sum()), int(t["sales"].sum()))

b = t.groupby("store", dropna=False)["sales"].sum()
print(len(b), b.tolist())

print(t.groupby("store").size().tolist())
print(t.groupby("store", dropna=False).size().tolist())
print(int(t["store"].count()), len(t))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `u = pd.DataFrame({"k": ["a", None], "v": [1, 2]})`, `u.groupby("k")["v"].sum().tolist()` is `[1]` and
`u.groupby("k", dropna=False)["v"].sum().tolist()` is `[1, 2]`: the missing-key group comes last.

## After you answer

- Which number on line 2 tells you that sales were lost, and how large is the loss?
- `count()` on the `store` column and `size()` of the groups both skip something. What exactly?
