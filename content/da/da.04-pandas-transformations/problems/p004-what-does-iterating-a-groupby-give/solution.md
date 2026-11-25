## Approach

Group the labels by `k` first: `a` → labels 1, 3, 5; `b` → 0, 4; `c` → 2.

1. The default loop goes in sorted key order and gives each sub-table: `a 3 [2, 4, 6]`, `b 2 [1, 5]`, `c 1 [3]`.
2. With `sort=False` the groups come in the order their key first appears in the column: `b`, `a`, `c`.
3. `ngroups` is 3, and `get_group("b")` is the sub-table of `b` with its original labels `[0, 4]`.
4. Grouping by a **list** with one column gives one-element tuples as keys in pandas 3: `('a',)`. The `break` stops after
   the first group.

## Output

```text
a 3 [2, 4, 6]
b 2 [1, 5]
c 1 [3]
['b', 'a', 'c']
3 [0, 4]
('a',) [1, 3, 5]
```

## Another way

`df.groupby("k").groups` is a dictionary from each key to its row labels, a quick way to see all groups at once.
