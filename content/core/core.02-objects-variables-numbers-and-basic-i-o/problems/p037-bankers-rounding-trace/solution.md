## Walkthrough

| Expression | Result | Why |
|---|---|---|
| `round(0.5)` | `0` | tie, 0 is even |
| `round(1.5)` | `2` | tie, 2 is even |
| `round(2.5)` | `2` | tie, 2 is even |
| `round(-2.5)` | `-2` | tie, -2 is even |
| `round(3.5)` | `4` | tie, 4 is even |
| `round(2.675, 2)` | `2.67` | stored as 2.67499999..., not a tie, so it goes down |
| `round(0.125, 2)` | `0.12` | 1/8 is exact in binary, a true tie; 2 is even |
| `round(1234, -2)` | `1200` | nearest hundred |
| `round(1250, -2)` | `1200` | tie between 1200 and 1300; 12 is even |
| `round(7.6)` | `8` | one argument: returns an int |
| `round(7.6, 0)` | `8.0` | two arguments: keeps the float type |
| `int(7.6)` | `7` | truncation toward zero |
| `int(-7.6)` | `-7` | truncation toward zero, not down to -8 |

## Why "banker's" rounding

Always rounding halves up adds a small upward bias when you round many values. Rounding halves
to even sends half of them up and half down on average. IEEE 754 and Python use it by default.
