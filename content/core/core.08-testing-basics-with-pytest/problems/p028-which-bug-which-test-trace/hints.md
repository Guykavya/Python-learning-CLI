## Hint 1

Take one version at a time. Find the single changed line, then ask: for which inputs does it give a different answer from the correct code? Only tests using those inputs can fail.

## Hint 2

Version B: the tests use 31, 90 and 91 minutes: compute `extra // 60` for each (extra is 1, 60 and 61). Version E: which inputs are `<= 31` but not `<= 30`? Version D: what does `fee(-5)` give when the check is gone?

## Hint 3

Version C only differs from the correct code when `hours * 10` is above 100. Which test uses a long stay? Version F is the reference and everything passes.
