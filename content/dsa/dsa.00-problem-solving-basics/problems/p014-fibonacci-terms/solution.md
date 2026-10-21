## Approach

Keep two variables: `a`, the term to print now, and `b`, the term after it. After printing `a`, slide the window
one step forward: the new `a` is the old `b`, and the new `b` is the old `a + b`. The tuple assignment
`a, b = b, a + b` computes the right-hand side completely before changing either variable, so no old value is lost.

Each term is printed with `end=" "` to stay on one line. After the loop, a single `print()` ends the line.
The checker ignores a trailing space at the end of the line. For `n = 0` the loop never runs and nothing is printed.

## Trace

Input `6`.

| Iteration | `a` (printed) | `b` | new `a` | new `b` |
|---|---|---|---|---|
| 1 | 0 | 1 | 1 | 1 |
| 2 | 1 | 1 | 1 | 2 |
| 3 | 1 | 2 | 2 | 3 |
| 4 | 2 | 3 | 3 | 5 |
| 5 | 3 | 5 | 5 | 8 |
| 6 | 5 | 8 | 8 | 13 |

Output: `0 1 1 2 3 5`.

## Code

```python
n = int(input())
a, b = 0, 1
for _ in range(n):
    print(a, end=" ")
    a, b = b, a + b
if n > 0:
    print()
```

## Complexity

`n` steps, each a single addition: O(n). Only two numbers are kept, so O(1) extra memory.

## Another way

If you want no trailing space at all, print the separator *before* every term except the first:

```python
n = int(input())
a, b = 0, 1
for i in range(n):
    if i > 0:
        print(" ", end="")
    print(a, end="")
    a, b = b, a + b
if n > 0:
    print()
```

This matters when a checker compares output character by character. Without tuple assignment you can also use a
temporary variable: `nxt = a + b`, then `a = b`, then `b = nxt`. It does the same thing in three lines.

## Edge cases

- `n = 0`: no output.
- `n = 1`: just `0`.
- `n = 2`: `0 1`. Many off-by-one solutions print `0 1` even for `n = 1` because they print the first two terms before the loop.
