# Write tests: average (with an error case)

Test this function (import it with `from target import average`):

```python
def average(numbers):
    """Return the mean of a non-empty list of numbers. Raise ValueError if it is empty."""
    if not numbers:
        raise ValueError("cannot average an empty list")
    return sum(numbers) / len(numbers)
```

Your tests must check the **normal results** and the **error case**:

- use `pytest.raises(ValueError, match="empty")` so that the test checks both the exception type
  **and** its message (chapter section 10). You need `import pytest`;
- a version that returns `0` for an empty list, a version that lets a `ZeroDivisionError` escape,
  and a version with the wrong message must all be caught;
- two further buggy versions give wrong averages.

Write at least 4 test functions.

**How this is checked.** Your `solution.py` is a file of pytest tests (chapter section 6). The
checker copies it next to the function above (saved as `target.py`) and runs real pytest, first on
the **correct** function (all your tests must pass), then on several **buggy copies** of it (at
least one of your tests must fail on each). Save the function as `target.py` in your folder
and run `python -m pytest solution.py` to try your tests yourself.
