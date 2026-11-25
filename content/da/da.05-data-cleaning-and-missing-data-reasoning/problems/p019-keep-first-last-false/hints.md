## Hint 1

Group the rows by id: which row ids belong to `a`, to `b`, to `c`, to `d`, and to the missing id? For each group,
`first` keeps its earliest row, `last` keeps its latest row, `False` keeps a row only if its group has exactly one member.
Remember that missing ids count as one group for `drop_duplicates` and `duplicated`.

## Hint 2

```text
groups:  a -> rows 1 3 6 | b -> rows 2 5 | c -> row 4 | d -> row 7 | missing -> rows 8 9
first: earliest of each group, listed in the table's original order
last : latest of each group, in the original order
False: only the groups with one row: c and d
line 4: duplicated(keep="first") counts the repeats; duplicated(keep=False) counts every member of a group of two or more
```
