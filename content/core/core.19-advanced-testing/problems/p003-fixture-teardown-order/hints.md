## Hint 1

For `test_one(session, cache)` pytest first sets up the fixtures **in the order of the
parameters**, but a fixture's own dependencies come first. What does `session` need before it
can start?

## Hint 2

Teardown runs in the **reverse** order of setup. And a failing test does not skip teardown.

```
test_one:  setup db, session, cache   -> test -> teardown cache, session, db
test_two:  setup cache                -> test (fails) -> teardown cache
last line: print the exit code (1 if any test failed)
```
