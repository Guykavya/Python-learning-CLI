## Approach


Seven runs: `test_plain`, then `test_letter[x]`, `test_number[x-1]`, `test_number[x-2]`, then
`test_letter[y]`, `test_number[y-1]`, `test_number[y-2]`. Pytest reordered the tests: with the
module-scoped parameter `letter`, all `x` tests run before all `y` tests, so `letter` is built
and destroyed exactly once per parameter and the output shows `letter x up` ... `letter x down`
before `letter y up`. The module-scoped autouse `banner` goes up first and down last. The
function-scoped autouse `tick` surrounds every run, and sits **inside** the `letter` fixture
(wider scope first). In `test_number`, the fixture `number` is set up after `tick` and `letter`
(a function-scoped fixture that depends on a module-scoped one), and the line "number for"
appears before the test prints.


## Output

```text
module autouse up
  tick up
  test_plain
  tick down
  letter x up
  tick up
  test_letter x
  tick down
  tick up
  number for x
  test_number 1
  tick down
  tick up
  number for x
  test_number 2
  tick down
  letter x down
  letter y up
  tick up
  test_letter y
  tick down
  tick up
  number for y
  test_number 1
  tick down
  tick up
  number for y
  test_number 2
  tick down
  letter y down
module autouse down
pytest exit code 0
```
