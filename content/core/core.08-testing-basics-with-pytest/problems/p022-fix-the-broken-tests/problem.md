# Fix the broken test file

A teammate wrote tests for `median` (the function is below) and complains that "the tests are
flaky and two of them even pass when the code is wrong". The file is in `starter.py`. It has
**six** separate mistakes. Find and fix them all in `solution.py`. Each mistake is one of:

- a wrong **expected value** (the test is wrong, the function is right: work it out by hand);
- an assert that can **never fail**;
- a test that **checks nothing**;
- two tests with the **same name**;
- a test whose name pytest **does not collect**;
- a `pytest.raises` block that does more than it should.

```python
def median(numbers):
    """Middle value of a non-empty list. For an even count, the mean of the two middle values."""
    if not numbers:
        raise ValueError("median of an empty list")
    ordered = sorted(numbers)
    mid = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2
```

Your fixed file must pass on the correct function, must fail on four buggy versions of it, and
must pass the checker's own review of your test file: no tuple asserts, every test has an
assert or a `with`, no misspelled test names, and one call inside each `pytest.raises` block.
Keep the same import line (`from target import median`).

**How this is checked.** Your `solution.py` is a file of pytest tests (chapter section 6). The
checker copies it next to the function above (saved as `target.py`) and runs real pytest, first on
the **correct** function (all your tests must pass), then on several **buggy copies** of it (at
least one of your tests must fail on each). Save the function as `target.py` in your folder
and run `python -m pytest solution.py` to try your tests yourself.
