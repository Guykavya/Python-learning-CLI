## Hint 1

What does `lines.groupby(["store_id", "channel"])["revenue"].sum()` return: a frame or a Series, and what is its index?
Which argument of `groupby` keeps the keys as ordinary columns from the start? Does `groupby` accept a plain string as
well as a list?

## Hint 2

```text
if keys is a string: keys = [keys]          (optional: groupby takes both)
result = lines.groupby(keys, as_index=False)["revenue"].sum()
         # or: lines.groupby(keys)["revenue"].sum().reset_index()
groupby sorts by the keys by default, so the rows are already in order
```
