## Walkthrough

| Code | Output | Why |
|---|---|---|
| `a, b` after `a += [3]` | `[1, 2, 3] [1, 2, 3]` | in-place change of the shared list |
| `a, b` after `a = a + [4]` | `[1, 2, 3, 4] [1, 2, 3]` | new list; only `a` moved |
| `t, u` | `(1, 2, 3) (1, 2)` | tuples cannot change, so `+=` made a new tuple |
| `s, r` | `hi! hi` | strings are immutable too |
| `x, y` after `y[0].append(1)` | `[[0, 1]] [[0, 1], [0, 1]]` | all three slots refer to one inner list |
| `x, y` after `y[1] = 5` | `[[0, 1]] [[0, 1], 5]` | replacing a slot of `y` touches nothing else |
| `m` after `n += [2]` | `[[1, 2], [1, 2]]` | both slots refer to `n`, which grew |
| `m, n` after `n = n + [3]` | `[[1, 2], [1, 2]] [1, 2, 3]` | `n` now names a new list; `m` keeps the old one |
