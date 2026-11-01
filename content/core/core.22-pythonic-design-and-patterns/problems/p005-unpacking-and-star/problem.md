# Unpacking and the star

Python lets you take a sequence apart in one line, so you do not need `p[0]`, `p[1]` ...
Names say more than numbers.

```python
x, y, z = point                    # tuple unpacking
a, b = b, a + b                    # swap / update together, no temporary variable
first, *rest = items               # *rest is always a list
_, *middle, _ = items              # drop the ends
(x1, y1), (x2, y2) = segment       # nested unpacking
merged = defaults | user           # dict merge (3.9+), or {**defaults, **user}
```

`starter.py` has seven working functions that use index numbers, a temporary variable and
`.copy()` + `.update()`. Copy it to `solution.py` and rewrite them with unpacking. Keep
names and parameters; behaviour must not change.

Checks on your code:

- `describe_point`, `split_head_tail`, `trim_ends`, `swap_pairs`, `distance_between` must not use
  numeric subscripts like `x[0]`, `x[1]` or `x[-1]` (slices such as `x[1:]` are not a goal here
  but starred unpacking is: use `*` in `split_head_tail` and `trim_ends`).
- `fib` must update both variables in one tuple assignment.
- `merge_settings` must use `|` or `**` unpacking.

**Example**

```python
split_head_tail([1, 2, 3])        # (1, [2, 3])
trim_ends([1, 2, 3, 4])           # [2, 3]
distance_between(((0, 0), (3, 4)))  # 5.0
merge_settings({"a": 1}, {"a": 2}, {"b": 3})   # {'a': 2, 'b': 3}
```
