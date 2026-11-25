## Hint 1

Write the rows of each group with their labels: which labels have `k == "a"`? In what order do the groups come with
the default `sort=True`, and in what order with `sort=False`?

## Hint 2

```text
groups (sorted):  a -> labels 1, 3, 5 (v 2, 4, 6);  b -> labels 0, 4 (v 1, 5);  c -> label 2 (v 3)
sort=False:       order of first appearance in the column k
get_group("b"):   the sub-table of b, original labels
groupby(["k"]):   a list of keys -> the key is a tuple, even with one element (pandas 3)
```
