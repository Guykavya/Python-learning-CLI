## Walkthrough

- The first `test_double` is replaced by the second one, so only the second runs, and `double(3) == 7` is false: FAILED. The silently lost first test is the danger.
- `testtriple` starts with `test` (underscore not needed): collected, `double(1) == 2`: PASSED.
- `tests_helper` also starts with `test`: collected and PASSED, even though the author meant it as a helper.
- `Test_upper` starts with a capital `T`: not collected, never runs.
- `helper_test` starts with `helper`: not collected. It would fail if it ran.
- `test_returns_nothing` checks nothing: PASSED.
- `test_error` raises `RuntimeError`: FAILED.
- `test_extra_argument(n)`: pytest looks for a fixture named `n`, finds none: ERROR.
- `test_last`: `double(-1)` is `-2`: PASSED.

## The exact output

```text
test_double FAILED
testtriple PASSED
tests_helper PASSED
test_returns_nothing PASSED
test_error FAILED
test_extra_argument ERROR
test_last PASSED
2 failed, 4 passed, 1 error
```
