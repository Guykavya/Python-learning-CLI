## Walkthrough

| Code | Output | Why |
|---|---|---|
| `list(k)` | `['a', 'b', 'c']` | the view sees the key added after it was made |
| `sum(v)` | `6` | the values view sees 3 as well |
| `len(it), len(snap)` | `3 2` | `snap` is a list made before `c` was added |
| `list(k), "a" in k` | `['b', 'c'] False` | `a` was deleted |
| `list(d)` | `['b', 'c', 'a']` | re-adding `a` puts it at the end |
| `("a", 10) in it` | `True` | items views support `in` on pairs |
| `e` | `{'b': 0, 'c': 3, 'a': 10, 'z': 26}` | right side wins for `b`; `b` keeps its place; `z` is added at the end |
| `list(v)` | `[20, 3, 10]` | `d` was updated in place, and `v` shows it |
| `k == {...}` | `True` | key views compare like sets: order does not matter |
