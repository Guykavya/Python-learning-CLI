## Walkthrough

| test | v1 `return 0` | v2 `numbers[0]` | v3 `best = 0` | v4 |
|---|---|---|---|---|
| picks the biggest `[3,1,2]` -> 3 | fail | pass | pass | pass |
| single item `[5]` -> 5 | fail | pass | pass | pass |
| negatives `[-4,-2,-9]` -> -2 | fail | fail (-4) | fail (0) | pass |
| empty raises | fail (nothing raised) | fail (IndexError escapes) | fail (returns 0) | pass |
| biggest is last `[1,2,9]` -> 9 | fail | fail (1) | pass | pass |

Version 3 shows why `best = 0` is a bug: the starting value belongs to the data, not to you. Version 2 raises `IndexError` for `[]`, which is not the `ValueError` the test expects, so it fails too.

## The exact output

```text
version 1: 5 failed
version 2: 3 failed, 2 passed
version 3: 2 failed, 3 passed
version 4: 5 passed
```
