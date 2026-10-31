## Hint 1

Go test by test and keep two counters on paper: how many times `per_test` has been set up, and
how many times `per_module` has. Which counter can only ever be 1?

## Hint 2

A module-scoped fixture is created the **first time** a test asks for it, and torn down only
after the last test in the file. Where does that teardown line appear in the output? Also: when a
test asks for a wide-scope and a narrow-scope fixture, which one does pytest set up first,
whatever the order of the parameters?

```
test_a: per_module set up (#1) FIRST, then per_test #1
test_b: per_test #2, per_module reused
test_c: per_module reused (no per_test)
test_d: per_test #3
after test_d: module teardown, then the exit code line
```
