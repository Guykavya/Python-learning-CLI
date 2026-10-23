# Write tests: sign (with parametrize)

Test this function. Import it with `from target import sign`.

```python
def sign(n):
    """Return 1 for positive numbers, -1 for negative numbers, 0 for zero."""
    if n > 0:
        return 1
    if n < 0:
        return -1
    return 0
```

This time the rule is: use **`@pytest.mark.parametrize`** (chapter section 9) for your cases, with
one table of `(number, expected)` rows. The checker looks for the word `parametrize` in your
file. The table must be rich enough to catch four hidden bugs: think about zero, both borders of
zero (`1` and `-1`), big numbers and floats like `0.5`.

You will need `import pytest` at the top of your file. Write at least 2 test functions.

**How this is checked.** Your `solution.py` is a file of pytest tests (chapter section 6). The
checker copies it next to the function above (saved as `target.py`) and runs real pytest, first on
the **correct** function (all your tests must pass), then on several **buggy copies** of it (at
least one of your tests must fail on each). Save the function as `target.py` in your folder
and run `python -m pytest solution.py` to try your tests yourself.
