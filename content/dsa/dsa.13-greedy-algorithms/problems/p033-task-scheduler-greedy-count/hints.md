## Hint 1

Take the most frequent letter, say `A` appearing `f` times. Its copies must be at least `n + 1` units apart (start to start). Draw them as the first column of a table with `f` rows and `n + 1` columns:

```text
A . .        (n = 2, f = 3)
A . .
A
```

Every row except the last is a full block of `n + 1` units. How many units does that table cover? Which tasks can sit in the `.` cells?

## Hint 2

The first `f - 1` rows take `(f - 1) * (n + 1)` units. The last row holds one copy of **each letter that also appears `f` times** (call that number `m`): they must come after their own `(f - 1)`-th copy. So the length is at least `(f - 1) * (n + 1) + m`. Fill the other letters into the `.` cells column by column, top to bottom, the most frequent ones first; a letter with fewer than `f` copies then never lands twice in one row, and its copies stay at least `n + 1` apart.

## Hint 3

If there are more tasks than cells, the table just gets wider: the extra tasks go into the rows without any idle unit, and the answer is simply `len(tasks)` (you can never beat one task per unit). So:

```
if no tasks: return 0
f = largest count
m = number of letters with count f
return max(len(tasks), (f - 1) * (n + 1) + m)
```
