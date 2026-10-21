## Walkthrough

| Code | Output | Why |
|---|---|---|
| `g` | `[[0, 5, 0], [0, 5, 0]]` | both slots refer to one row |
| `h` | `[[0, 5, 0], [0, 0, 0]]` | the comprehension made two rows |
| `m, row` | `[[7, 0], [7, 0]] [7, 0]` | `m` holds two references to `row` |
| `m` after `m[0] = [1, 1]` and `m[1][1] = 9` | `[[1, 1], [7, 9]]` | slot 0 now refers to a new list; slot 1 is still `row` |
| `k` | `[['x'], ['x', 'y'], ['x']]` | `append` changed the shared list; slot 1 was replaced by a new list |
| identity | `True False` | slots 0 and 2 still share; slot 1 is different now |

Memory picture for `g`:

```
g --> [ o , o ]
        |   |
        +---+--> [0, 5, 0]
```
