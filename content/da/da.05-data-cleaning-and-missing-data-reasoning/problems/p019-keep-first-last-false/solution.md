## Approach

The groups are `a` = rows 1, 3, 6; `b` = rows 2, 5; `c` = row 4; `d` = row 7; and **missing** = rows 8, 9 (for
`duplicated` and `drop_duplicates`, a missing value equals a missing value).

- `keep="first"` keeps the earliest row of each group: 1, 2, 4, 7, 8. Rows come out in the original order.
- `keep="last"` keeps the latest: 4 (c), 5 (b), 6 (a), 7 (d), 9 (missing): `[4, 5, 6, 7, 9]`.
- `keep=False` removes **every** row that has a partner and keeps only the groups of one: 4 and 7.
- Last line: the repeats after the first copy are rows 3, 5, 6 and 9 (4 rows); every member of a group of two or more is
  rows 1, 3, 6, 2, 5, 8, 9 (7 rows).

```text
first [1, 2, 4, 7, 8]
last [4, 5, 6, 7, 9]
False [4, 7]
4 7
```

## Complexity

Not applicable.

## Another way

After you wrote the answer, run the code and then try `df.dropna(subset=["id"]).drop_duplicates(subset="id")`: the
missing ids disappear first, so the row 8 is gone too. If a missing key means "unknown person", that is what you want:
two unknown people are not the same person.
