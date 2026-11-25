## Hint 1

Go through the four expressions one at a time: is the thing inside the brackets a single name, a list of names, a slice, or a True/False Series? Each one has a different meaning (one column, several columns, rows by position, rows by condition).

## Hint 2

```text
df["a"]          one name      -> Series, 4 values            -> Series (4,)
df[["a"]]        list of names -> DataFrame, one column       -> DataFrame (4, 1)
df[1:3]          slice         -> rows at positions 1, 2      -> DataFrame (2, 2)
df[df["a"] > 1]  True/False    -> rows where a > 1 (2, 3, 4)  -> DataFrame (3, 2)
```
