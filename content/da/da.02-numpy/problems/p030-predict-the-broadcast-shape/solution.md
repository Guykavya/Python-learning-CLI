## Approach

Right-align and compare each axis:

| pair | padded | axis by axis | result |
|---|---|---|---|
| `(3, 1)` + `(4,)` | `(3, 1)` / `(1, 4)` | 1 vs 4 → 4; 3 vs 1 → 3 | `(3, 4)` |
| `(5, 1, 4)` + `(3, 1)` | `(5, 1, 4)` / `(1, 3, 1)` | 4/1 → 4; 1/3 → 3; 5/1 → 5 | `(5, 3, 4)` |
| `(2, 3)` + `(3, 2)` | same length | last axis 3 vs 2 | error |
| `(8, 1, 6, 1)` + `(7, 1, 5)` | `(8, 1, 6, 1)` / `(1, 7, 1, 5)` | 1/5, 6/1, 1/7, 8/1 | `(8, 7, 6, 5)` |
| `(4, 3)` + `(4,)` | `(4, 3)` / `(1, 4)` | last axis 3 vs 4 | error |
| `(6,)` + `(6, 1)` | `(1, 6)` / `(6, 1)` | 6/1 → 6; 1/6 → 6 | `(6, 6)` |
| `(2, 1, 3)` + `(4, 3)` | `(2, 1, 3)` / `(1, 4, 3)` | 3/3; 1/4 → 4; 2/1 → 2 | `(2, 4, 3)` |
| `(3, 4)` + `(3, 4, 1)` | `(1, 3, 4)` / `(3, 4, 1)` | 4/1 → 4; 3 vs 4 | error |

The last case is the sneaky one: the trailing axis is fine (4 vs 1), and the failure is on the middle axis.

## Code

The expected output is in `expected.txt`, produced by running the program. Check any pair yourself with `np.broadcast_shapes((3, 4), (3, 4, 1))`.

## Complexity

Not applicable. Note that the arrays are tiny (`np.zeros(shape)`); broadcasting itself never copies the stretched input (stride 0, Ch. 11.8), only the result is new.

## Another way

`np.broadcast_shapes(*shapes)` returns the shape or raises `ValueError` without creating any array, which is the right tool for a quick check before a big computation.
