## Hint 1

First list the tests that will run: `test_plain` (1 run), `test_letter` (2 runs: x and y),
`test_number` (2 runs from `n` times 2 from `letter` = 4 runs). That is 7 runs in total. Which
fixtures does each run need?

## Hint 2

Rules to apply, in this order of importance:
1. Autouse and wide-scope fixtures are set up first, and torn down last.
2. A module-scoped parametrized fixture is rebuilt for each parameter; pytest groups the tests
   by parameter to minimise rebuilds, so all `x` runs come before all `y` runs. Tests that do
   not use `letter` (here `test_plain`) are not part of any group and keep their place first.
3. Function-scoped `tick` goes up and down around every single test.

```
module autouse up
test_plain run (tick up/down around it)
letter x up -> every run with x (tick around each) -> letter x down
letter y up -> every run with y -> letter y down
module autouse down
```
