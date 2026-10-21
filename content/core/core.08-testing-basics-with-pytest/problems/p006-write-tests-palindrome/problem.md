# Write tests: is_palindrome

Write tests in `solution.py` for this function (import it with `from target import is_palindrome`):

```python
def is_palindrome(text):
    """True if text reads the same backwards, ignoring upper/lower case and spaces."""
    cleaned = text.lower().replace(" ", "")
    return cleaned == cleaned[::-1]
```

Your tests must pass on the correct function and fail on each of **five** buggy versions. Think
about what makes palindrome checks go wrong: letter case, spaces, very short input, words that
only *look* symmetric, and so on. Write at least 4 test functions with a message on every assert.

**How this is checked.** Your `solution.py` is a file of pytest tests (chapter section 6). The
checker copies it next to the function above (saved as `target.py`) and runs real pytest, first on
the **correct** function (all your tests must pass), then on several **buggy copies** of it (at
least one of your tests must fail on each). Save the function as `target.py` in your folder
and run `python -m pytest solution.py` to try your tests yourself.
