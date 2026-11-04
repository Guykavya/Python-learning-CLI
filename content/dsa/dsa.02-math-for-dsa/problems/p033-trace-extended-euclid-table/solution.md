## Walkthrough: table(240, 46)

| row | q | r | s | t | check `240*s + 46*t` |
|---|---|---|---|---|---|
| 0 | - | 240 | 1 | 0 | 240 |
| 1 | - | 46 | 0 | 1 | 46 |
| 2 | 5 | 10 | 1 | -5 | 240 - 230 = 10 |
| 3 | 4 | 6 | -4 | 21 | -960 + 966 = 6 |
| 4 | 1 | 4 | 5 | -26 | 1200 - 1196 = 4 |
| 5 | 1 | 2 | -9 | 47 | -2160 + 2162 = 2 |
| 6 | 2 | 0 | 23 | -120 | 5520 - 5520 = 0 |

The row before the zero row is `(r, s, t) = (2, -9, 47)`: `gcd = 2`, `x = -9`, `y = 47`. This agrees with the recursive
version's answer in the previous problem: `ext(240, 46) = (2, -9, 47)`.

The same method gives the other two tables. For `table(17, 0)` there is no pass at all, so only the two header rows print, then
`gcd 17 x 1 y 0`.

## Output

```
q r s t
- 240 1 0
- 46 0 1
5 10 1 -5
4 6 -4 21
1 4 5 -26
1 2 -9 47
2 0 23 -120
gcd 2 x -9 y 47
check 2
---
q r s t
- 99 1 0
- 78 0 1
1 21 1 -1
3 15 -3 4
1 6 4 -5
2 3 -11 14
2 0 26 -33
gcd 3 x -11 y 14
check 3
---
q r s t
- 17 1 0
- 0 0 1
gcd 17 x 1 y 0
check 17
```

## Key ideas

- Every row satisfies `r = a*s + b*t`. That is the invariant that makes the final row the answer.
- The last row (`r = 0`) has `s = b/g` and `t = -a/g` up to sign: the "other" solutions of `a*x + b*y = 0`.
- The `r` column is exactly the Euclid remainder sequence: 240, 46, 10, 6, 4, 2, 0.
