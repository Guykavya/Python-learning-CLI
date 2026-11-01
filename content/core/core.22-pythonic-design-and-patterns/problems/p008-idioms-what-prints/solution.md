## Approach

Evaluate each `print` separately and keep the one piece of shared state (`calls`) in mind.

| Line of program | Reasoning | Output |
|---|---|---|
| `1 < 2 < 3`, `1 < 3 < 2` | `1<2 and 2<3`; `1<3 and 3<2` | `True False` |
| `5 > 3 == 3`, `2 < 1 < 5` | `5>3 and 3==3`; the first test `2<1` fails, so stop | `True False` |
| `name or "guest"`, `0 or None`, `[] or [0]` | `""` falsy so `"guest"`; `0` falsy so `None`; `[]` falsy so `[0]`. `repr` adds quotes | `'guest' None [0]` |
| `1 and 2`, `0 and 2`, `None or 0` | `1` truthy so `2`; `0` falsy so `0`; `None` falsy so `0` | `2 0 0` |
| `config.get("a", default())`, `config.get("b", default())`, `len(calls)` | both `default()` calls run before `get` (eager), so `calls` has 2 entries when `len` runs; first get finds `1`, second uses `"d"` | `1 d 2` |
| `sorted(words, key=len)` | lengths 2,1,2,1,2; length-1 words first (`a`, `d`), then length-2 in original order (`bb`, `cc`, `aa`) | `['a', 'd', 'bb', 'cc', 'aa']` |
| same, `reverse=True` | longest first; ties keep original order (reverse keeps stability) | `['bb', 'cc', 'aa', 'a', 'd']` |
| `zip([1,2,3], "ab")` | stops at the shorter | `[(1, 'a'), (2, 'b')]` |
| `a, b = b, a + b` three times | (1,2) -> (2,3) -> (3,5) -> (5,8) | `5 8` |
| `[[0] * 2] * 2`, set `grid[0][0]` | both rows are the same list object | `[[9, 0], [9, 0]]` |
| `[[0] * 2 for _ in range(2)]` | each row is a fresh list | `[[9, 0], [0, 0]]` |
| `any([])`, `all([])`, `any([0, ""])`, `all([1, "x"])` | no items to be true; nothing to be false; none truthy; all truthy | `False True False True` |
| `y += [4]`, `z = x + [5]` | `+=` on a list extends in place, so `x` is `[1,2,3,4]` and `y is x`; `+` creates a new list | `[1, 2, 3, 4] True False` |
| `[i for i in range(5) if i % 2]`, `[i*i ...][-1]` | odd numbers 1, 3; last square is 2*2 | `[1, 3] 4` |

## Full output

```
True False
True False
'guest' None [0]
2 0 0
1 d 2
['a', 'd', 'bb', 'cc', 'aa']
['bb', 'cc', 'aa', 'a', 'd']
[(1, 'a'), (2, 'b')]
5 8
[[9, 0], [9, 0]]
[[9, 0], [0, 0]]
False True False True
[1, 2, 3, 4] True False
[1, 3] 4
```

## Another way

Run it, then explain every line you got wrong. The surprising ones (`default()` running
eagerly, `[[0]*2]*2`, `all([])`) are the ones to turn into habits: use `d[k] if k in d else f()`
or a lazy default when the default is expensive, and build grids with a comprehension.
