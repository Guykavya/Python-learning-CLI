## Hint 1

Which rows does `df["n"] > 5` keep, and what are their labels in the original frame? Does a filter renumber the rows?

## Hint 2

```text
df index 0,1,2,3   n = 5,6,7,8
kept = rows with n > 5  -> labels 1, 2, 3   (shape (3, 2))
kept.loc[0]        -> label 0 was filtered out    -> KeyError
kept["n"].iloc[0]  -> first row kept (label 1)    -> 6
kept.loc[2, "n"]   -> label 2                     -> 7
fresh              -> labels 0,1,2 again          -> fresh.loc[0, "n"] = 6
kept.reset_index() -> old labels become a column named "index"
```
