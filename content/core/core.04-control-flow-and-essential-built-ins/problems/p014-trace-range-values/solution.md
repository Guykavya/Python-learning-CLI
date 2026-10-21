## Walkthrough

| Code | Result | Why |
|---|---|---|
| `range(4)` | `[0, 1, 2, 3]` | start defaults to 0, stop 4 excluded |
| `range(3, 8, 2)` | `[3, 5, 7]` | 9 would pass 8 |
| `range(8, 3, -2)` | `[8, 6, 4]` | 2 would pass 3 going down |
| `range(5, 5)` | `[]` | start equals stop |
| `range(-3, 0)` | `[-3, -2, -1]` | 0 excluded |
| `range(0, -3)` | `[]` | step +1 cannot go down |
| `len(range(1, 11))` | `10` | 11 - 1 |
| `len(range(0, 10, 3))` | `4` | 0, 3, 6, 9 |
| sum of 1, 3, 5 | `9 5` | `i` keeps its last value, 5 |
| `range(10, 0, -4)` | `10 6 2` | -2 would pass 0 |
