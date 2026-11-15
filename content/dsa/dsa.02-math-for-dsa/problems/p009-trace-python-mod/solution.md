## Walkthrough

| line | exact quotient | floor `//` | `%` = `a - q*b` |
|---|---|---|---|
| `17, 5` | 3.4 | 3 | 17 - 15 = 2 |
| `-17, 5` | -3.4 | -4 | -17 + 20 = 3 |
| `17, -5` | -3.4 | -4 | 17 - 20 = -3 |
| `-17, -5` | 3.4 | 3 | -17 + 15 = -2 |

Other lines:

- `divmod(-17, 5)` is `(-4, 3)`, the same pair as `//` and `%`, printed as a tuple.
- `int(-17 / 5)` is `int(-3.4)` which **truncates** to `-3`. This is not `//`.
- `-7 % 7` and `0 % 7` are both 0.
- `(-3) % 10` and `-3 % 10` are both 7 (unary minus binds tighter than `%`). But `-(3 % 10)` is `-3`.
- `-2 ** 2` is `-4`; `(-2) ** 2` is `4`.
- `divmod(23, -4)`: exact quotient -5.75, floor -6, remainder `23 - (-6)(-4) = -1`. The check `-6 * -4 + -1 == 23` is `True`.
- `(7 - 10) % 12 = (-3) % 12 = 9`.
- `5 // 0.5` is `10.0` (a float, floor division of floats), and `7.5 % 2` is `1.5`.

Output:

```
3 2
-4 3
-4 -3
3 -2
(-4, 3)
-3
0 0
7
7
-3
-4 4
-6 -1 True
9
10.0 1.5
```

## Key idea

In Python, `a % m` with a positive `m` is always in `0 .. m - 1`, even for negative `a`. Subtracting something
and taking `% m` just works, so mod arithmetic needs no repair step. In C++ or Java you would have to add `m`
before taking the final `%`.
