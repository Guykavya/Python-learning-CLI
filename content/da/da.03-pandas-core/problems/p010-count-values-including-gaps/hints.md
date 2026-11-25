## Hint 1

What does `value_counts()` do with `None` by default, and which argument changes that? A different idea: what if you replaced the missing values by the text `"(missing)"` first? Which sort handles "count descending, then label ascending"?

## Hint 2

```text
labels = s with missing replaced by "(missing)"        (where / fillna on an object copy)
counts = labels.value_counts()
out    = DataFrame(label = counts.index, count = counts values)
out["share"] = out["count"] / len(s)
out = out.sort_values(["count", "label"], ascending=[False, True]).reset_index(drop=True)
```
