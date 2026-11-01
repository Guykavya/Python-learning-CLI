# Loops the Python way

`starter.py` has four small functions that work, but they are written the way a C programmer
would write them: `range(len(x))`, a hand-made counter, a "found" flag. Python has tools made
for exactly these jobs.

| You wrote | Python says |
|---|---|
| `for i in range(len(x)): ... x[i] ...` and you need the position | `for i, item in enumerate(x):` |
| two lists walked with one index | `for a, b in zip(xs, ys):` (stops at the shorter one) |
| a `found = False` flag set inside a loop | `any(...)` or `all(...)` |
| a counter you add 1 to | `sum(...)` over a generator expression |

Copy `starter.py` to `solution.py` and rewrite the four functions. **Behaviour must not
change.** Keep the names and parameters.

Your solution is also checked for structure:

- there must be **no `range(len(...))`** anywhere,
- `has_negative` and `count_equal_positions` must contain **no `for`/`while` statement**
  (a generator expression inside `any` or `sum` is fine),
- `enumerate` and `zip` must be used.

**Example**

```python
indexed_lines(["a", "b"])                    # ['1: a', '2: b']
add_lists([1, 2, 3], [10, 20])               # [11, 22]   (stops at the shorter list)
has_negative([3, -1, 4])                     # True
count_equal_positions([1, 2, 3], [1, 0, 3])  # 2
```
