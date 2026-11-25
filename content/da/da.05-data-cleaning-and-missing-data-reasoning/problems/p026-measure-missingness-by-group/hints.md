## Hint 1

How do you turn "is this value missing?" into something a group can add up? What do `size` and `sum` of that Boolean
column mean inside a group? Which call puts the group key back as a column and gives a fresh index, and how do you sort
by two columns with two different directions?

## Hint 2

```text
t = df.assign(_missing = df[col].isna()).groupby(by)["_missing"].agg(["size", "sum"])
rename -> rows, missing;  rate = missing / rows
reset_index()   (the key becomes a column)
sort_values([rate, by], ascending=[False, True]);  reset_index(drop=True)
make rows and missing plain integers
```
