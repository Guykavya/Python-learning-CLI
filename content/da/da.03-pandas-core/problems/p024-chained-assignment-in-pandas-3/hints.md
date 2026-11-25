## Hint 1

Ask of every statement: is it changing **the object itself** (a name for it, or `.loc` on the frame) or a **temporary result** (the output of `df[mask]` or `df["a"]`)? Under Copy-on-Write a temporary result is its own copy.

## Hint 2

```text
df[mask]["b"] = 0      changes the temporary df[mask]; df unchanged; one ChainedAssignmentError warning
s = df["a"]; s.iloc[0] = 99     s becomes [99,2,3], a copy on write; df["a"] stays [1,2,3]
df.loc[mask, "b"] = 0           one loc on df itself: rows with a > 1 get b = 0
y = x                           same object: y.iloc[0] = 9 changes x too
z = x.copy()                    separate object: z changes, x does not
```
