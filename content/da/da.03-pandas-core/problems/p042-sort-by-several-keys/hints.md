## Hint 1

`sort_values` accepts a **list** of columns and a list of directions of the same length (section 14.2). Which direction does each of your two keys need? And what does `na_position` control: the rows with a missing key come first or last by default?

## Hint 2

```text
df.sort_values(
    ["revenue", "seller"],
    ascending=[False, True],       # revenue high to low, names A to Z
    na_position="last",            # missing revenue at the end
    kind="stable",                 # equal rows keep their order
)
```
Do not call `reset_index`: the original labels are part of the expected answer.
