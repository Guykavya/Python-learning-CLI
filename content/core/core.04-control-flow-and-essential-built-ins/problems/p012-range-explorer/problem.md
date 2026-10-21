# Range explorer

Read three whole numbers, `start`, `stop` and `step`, one per line. Print what
`range(start, stop, step)` contains:

- Line 1: the numbers separated by single spaces, or `(empty)` if there are none.
- Line 2: `Count: <how many numbers>`.

If `step` is 0, print only `step cannot be 0` (a real `range` would crash).

**Examples**

| Input | Output |
|---|---|
| `1`, `10`, `3` | `1 4 7` and `Count: 3` |
| `5`, `0`, `-2` | `5 3 1` and `Count: 3` |
| `5`, `0`, `1` | `(empty)` and `Count: 0` |
