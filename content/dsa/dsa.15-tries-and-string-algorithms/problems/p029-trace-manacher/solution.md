## Approach

Fill `p` from left to right. Inside the rightmost palindrome, copy the mirror's radius (capped at `r - i`), then expand only beyond what is known.

## Expected output

```text
0 # 0 0 0 0
1 a 0 1 1 2
2 # 0 0 1 2
3 b 0 3 3 6
4 # 0 0 3 6
5 a 1 1 3 6
6 # 0 0 3 6
7 x 0 7 7 14
8 # 0 0 7 14
9 a 1 1 7 14
10 # 0 0 7 14
11 b 3 3 7 14
12 # 0 0 7 14
13 a 1 1 7 14
14 # 0 0 7 14
[0, 1, 0, 3, 0, 1, 0, 7, 0, 1, 0, 3, 0, 1, 0]
```

## Why

- `i = 1` (`a`): `#` and `#` match, then the left end is reached: `p = 1`, `(c, r) = (1, 2)`.
- `i = 3` (`b`): grows over `#a#` on both sides: `p = 3`, `(3, 6)`.
- `i = 5` (`a`): mirror 1, start `min(1, 1) = 1`; `b` against `x` fails: `p = 1`.
- `i = 7` (`x`): outside the box, expands all the way to both ends of `t`: `p = 7`, `(7, 14)`. The whole `abaxaba` is a palindrome.
- `i = 9, 11, 13`: mirrors 5, 3, 1 give 1, 3, 1; each expansion would read past index 14, so nothing is added.
- All `#` rows have radius 0 here: no two neighbouring characters of `abaxaba` are equal, so there is no even palindrome.

**After you answer.**

1. Rows 5, 9, 11 and 13 had a positive start. None of them grew: for row 5 the next comparison failed (`b` against `x`), and for rows 9, 11, 13 the palindrome already touched the end of `t`.
2. `p[11]` would need `t[7]` and `t[15]`; index 15 does not exist. The cap `r - i = 3` and the end of the string meet exactly there.
3. The longest is the whole string, length 7: the maximum of `p` is 7, at `i = 7`, starting at `(7 - 7) // 2 = 0`.

## Another way

Expand around every centre without copying (the starter of p026) and compare the arrays: the same `p`, but rows 9 to 13 then repeat comparisons the copy made unnecessary.
