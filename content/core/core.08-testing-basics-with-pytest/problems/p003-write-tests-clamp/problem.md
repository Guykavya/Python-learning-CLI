# Write tests: clamp

This time **you write the tests**. The function under test is:

```python
def clamp(x, low, high):
    """Return x limited to the range low..high (low <= high)."""
    if x < low:
        return low
    if x > high:
        return high
    return x
```

In `solution.py` write test functions (names start with `test_`) that check `clamp`. Import it
with `from target import clamp`.

Your tests must

1. **pass** on the correct function above, and
2. **fail** on each of five buggy versions of `clamp` that the checker tries. Each bug is a
   typical slip: one forgets a side, one mangles negative numbers, and so on. If a bug survives,
   the report names it, so you know which kind of case is missing.

Write at least 4 test functions. Give every `assert` a message that says what went wrong.

**How this is checked.** Your `solution.py` is a file of pytest tests (chapter section 6). The
checker copies it next to the function above (saved as `target.py`) and runs real pytest, first on
the **correct** function (all your tests must pass), then on several **buggy copies** of it (at
least one of your tests must fail on each). Save the function as `target.py` in your folder
and run `python -m pytest solution.py` to try your tests yourself.

**Example of one test**

```python
def test_value_inside_the_range_is_unchanged():
    assert clamp(5, 0, 10) == 5, "A value inside the range must come back unchanged."
```
