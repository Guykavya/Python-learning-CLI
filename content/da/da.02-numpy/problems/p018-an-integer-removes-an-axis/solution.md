## Approach

Apply the rule position by position:

| Index | Effect on `(3, 4, 5)` | Shape |
|---|---|---|
| `a[1]` | drop axis 0 | `(4, 5)` |
| `a[1:2]` | axis 0 becomes length 1 | `(1, 4, 5)` |
| `a[:, 1]` | drop axis 1 | `(3, 5)` |
| `a[:, [1]]` | axis 1 becomes length 1 | `(3, 1, 5)` |
| `a[..., 0]` | drop the last axis | `(3, 4)` |
| `a[None]` | insert 1 in front | `(1, 3, 4, 5)` |
| `a[1, :, 2]` | drop axes 0 and 2 | `(4,)` |
| `a[[0, 2]]` | axis 0 becomes length 2 | `(2, 4, 5)` |
| `a[:, None, :, 0]` | keep, insert 1, keep, drop | `(3, 1, 4)` |
| `a[1, 2, 3]` | drop everything | `()` |

A single element is a NumPy scalar with no axes, so its shape is the empty tuple `()`.

## Code

The expected output is in `expected.txt`, produced by running the program above.

## Complexity

All of these are views except `a[:, [1]]` and `a[[0, 2]]` (a list of positions copies).

## Another way

Keeping an axis of length 1 (`a[:, [1]]`, `a[1:2]`, `keepdims=True`) is how you keep an array ready for broadcasting against the original (Ch. 10.3 and 11).
