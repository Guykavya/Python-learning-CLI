## Walkthrough

| Line | Output | Why |
|---|---|---|
| `type(x), type(y)` | `<class 'int'> <class 'tuple'>` | `(7)` is just 7; the comma in `7,` makes a tuple |
| `y, len(y)` | `(7,) 1` | a one-item tuple prints with a trailing comma |
| `z + (1, 2)` | `(1, 2)` | `()` is the empty tuple |
| `p, q, r` | `1 [2, 3] 4` | the starred name collects a list |
| `a, b` (after the loop) | `3 5` | `(1,1)` to `(1,2)` to `(2,3)` to `(3,5)`, each step computed from the old values |
| `t` | `(1, [2, 99])` | the tuple's slots did not change; the list inside it did |
| `len(t[1])` | `2` | the inner list holds 2 and 99 |
