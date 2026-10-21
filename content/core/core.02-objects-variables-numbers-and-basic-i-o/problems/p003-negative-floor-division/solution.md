## Walkthrough

| Expression | Result | Why |
|---|---|---|
| `7 // 2` | `3` | 3.5 rounded down |
| `-7 // 2` | `-4` | -3.5 rounded **down** is -4, not -3 |
| `7 % 3` | `1` | 2 * 3 + 1 = 7 |
| `-7 % 3` | `2` | -7 // 3 is -3, and -3 * 3 + 2 = -7 |
| `7 % -3` | `-2` | 7 // -3 is -3, and -3 * -3 + (-2) = 7. The sign follows the divisor |
| `int(-3.5)` | `-3` | `int` truncates toward zero |
| `divmod(-7, 2)` | `(-4, 1)` | -4 * 2 + 1 = -7 |

## The rule to remember

In Python, the result of `%` always has the **same sign as the divisor**, because `//`
rounds toward negative infinity. C, Java and JavaScript truncate toward zero instead,
so the same expressions give different answers there.
