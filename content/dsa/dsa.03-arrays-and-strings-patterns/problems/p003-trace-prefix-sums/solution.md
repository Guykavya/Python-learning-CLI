## Walkthrough

| x | p after append | printed |
|---|---|---|
| 3 | [0, 3] | add 3 -> 3 |
| -1 | [0, 3, 2] | add -1 -> 2 |
| 4 | [0, 3, 2, 6] | add 4 -> 6 |
| 1 | [0, 3, 2, 6, 7] | add 1 -> 7 |
| 5 | [0, 3, 2, 6, 7, 12] | add 5 -> 12 |

| l r | p[r] | p[l-1] | answer | check by hand |
|---|---|---|---|---|
| 1 3 | p[3] = 6 | p[0] = 0 | 6 | 3 - 1 + 4 = 6 |
| 2 5 | p[5] = 12 | p[1] = 3 | 9 | -1 + 4 + 1 + 5 = 9 |
| 4 4 | p[4] = 7 | p[3] = 6 | 1 | just a[3] = 1 |

## Output

```
add 3 -> 3
add -1 -> 2
add 4 -> 6
add 1 -> 7
add 5 -> 12
p = [0, 3, 2, 6, 7, 12]
1 3 : 6 - 0 = 6
2 5 : 12 - 3 = 9
4 4 : 7 - 6 = 1
5 6
```

## Key ideas

- `p[i]` is the sum of the **first i** elements. That is why `p` has `n + 1` cells: `p[0]` is the empty sum.
- A totals list need not grow steadily: `-1` makes it go from 3 down to 2.
- `p[r] - p[l-1]` removes everything before position `l`. For `l = r` it leaves one element.
