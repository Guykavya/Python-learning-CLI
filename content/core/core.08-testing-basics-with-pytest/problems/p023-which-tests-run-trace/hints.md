## Hint 1

Make a list of every function name and mark whether it starts with lower-case `test`. Cross out the rest. Then look for names that appear twice: only the last definition counts.

## Hint 2

For each remaining test: does it contain an assert that is false? Does it raise a different exception? Does it have a parameter pytest cannot fill in?

## Hint 3

`test_returns_nothing` has no assert and no error, so it passes. `test_extra_argument(n)`: no fixture called `n` exists, so the test is an ERROR, not a FAILED.
