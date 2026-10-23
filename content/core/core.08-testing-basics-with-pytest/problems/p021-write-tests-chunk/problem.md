# Write tests: chunk

```python
def chunk(items, size):
    """Split a list into consecutive pieces of length size. The last piece may be shorter."""
    if size <= 0:
        raise ValueError("size must be positive")
    pieces = []
    for start in range(0, len(items), size):
        pieces.append(items[start:start + size])
    return pieces
```

Import with `from target import chunk`. A function that returns a **list of lists** and takes a
list can go wrong in many ways. The checker has six buggy versions. They include: dropping the
leftover items, accepting a bad size, giving the wrong error message, returning tuples, returning
`[[]]` for an empty list, and a version that **empties the list you pass in** (so check that your
input list is unchanged afterwards).

Use `pytest.raises(..., match=...)` for the error. Write at least 6 test functions.

**How this is checked.** Your `solution.py` is a file of pytest tests (chapter section 6). The
checker copies it next to the function above (saved as `target.py`) and runs real pytest, first on
the **correct** function (all your tests must pass), then on several **buggy copies** of it (at
least one of your tests must fail on each). Save the function as `target.py` in your folder
and run `python -m pytest solution.py` to try your tests yourself.
