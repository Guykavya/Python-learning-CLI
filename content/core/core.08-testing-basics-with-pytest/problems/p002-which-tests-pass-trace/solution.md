## Walkthrough

- `test_add_small`: `2 + 3 == 5`, PASSED.
- `test_add_negative`: `-1 + 1` is `0`, not `1`, so the assert fails: FAILED.
- `test_add_zero`: `0 == 0`, PASSED.
- `check_add_big` does not start with `test_`, so pytest never collects it. It would fail if it ran, but nobody runs it. That is a classic way to have a "test" that protects nothing.
- `test_add_float`: `0.5 + 0.25` is exactly `0.75` in binary floating point (both are sums of powers of 2), PASSED.
- `test_add_strings`: `"a" + "b"` is `"ab"`, PASSED.
- `test_add_mixed`: `"1" + 1` raises `TypeError` before the comparison happens. pytest reports an exception inside a test as FAILED.

## The exact output

```text
test_add_small PASSED
test_add_negative FAILED
test_add_zero PASSED
test_add_float PASSED
test_add_strings PASSED
test_add_mixed FAILED
2 failed, 4 passed
```
