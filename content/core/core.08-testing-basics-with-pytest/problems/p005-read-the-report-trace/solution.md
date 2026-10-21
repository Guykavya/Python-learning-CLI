## Walkthrough

The section header `test_discount_full` names the test. The `>` marker points at the failing assert, and the report's last location line says `test_discount.py:14`. The `E` line says `assert 0.0 == 8`: the function returned `0.0` (the left side, the computed value) and the test expected `8`. Since 100 percent off 80 is 0, the **function is right and the test is wrong**: whoever wrote `== 8` mixed up the numbers (a 90 percent discount leaves 8). A failing test is a signal, not a verdict: sometimes the test is the bug.

## The exact output

```text
failed test: test_discount_full
line: 14
function returned: 0.0
test expected: 8
wrong one: test
```
