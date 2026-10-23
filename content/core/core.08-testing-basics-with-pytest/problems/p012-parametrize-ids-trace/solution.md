## Walkthrough

- `test_add` has four rows. All four sums equal the expected values (`2.5 + 0.5` is exactly `3.0`). The ids are the values joined by `-`: `1-2-3`, `0-0-0`, `-1-1-0` (read it as `-1`, `1`, `0`) and `2.5-0.5-3.0`.
- `test_palindrome`: `level` and `noon` read the same backwards; `abc` does not, so only that row fails.
- `test_positive`: ids are `one` and `two`. The row `n = 1` fails (`1 > 1` is false), `n = 2` passes.
- `test_pair`: the bottom decorator (`y`) is applied first, so the id is `y-x`. Rows in order: `a-1`, `a-2`, `b-1`, `b-2` (`y` changes slowest, `x` fastest). Only `x = 2` with `y = "b"` builds `"2b"`, so `b-2` fails.

## The exact output

```text
test_add[1-2-3] PASSED
test_add[0-0-0] PASSED
test_add[-1-1-0] PASSED
test_add[2.5-0.5-3.0] PASSED
test_palindrome[level] PASSED
test_palindrome[abc] FAILED
test_palindrome[noon] PASSED
test_positive[one] FAILED
test_positive[two] PASSED
test_pair[a-1] PASSED
test_pair[a-2] PASSED
test_pair[b-1] PASSED
test_pair[b-2] FAILED
3 failed, 10 passed
```
