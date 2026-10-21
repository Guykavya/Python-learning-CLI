# Write tests: is_valid_password

```python
def is_valid_password(pw):
    """Valid: at least 8 characters, no spaces, and at least one digit, one lower and one upper letter."""
    if len(pw) < 8:
        return False
    if " " in pw:
        return False
    has_digit = False
    has_lower = False
    has_upper = False
    for ch in pw:
        if ch.isdigit():
            has_digit = True
        if ch.islower():
            has_lower = True
        if ch.isupper():
            has_upper = True
    return has_digit and has_lower and has_upper
```

A function with several rules needs a test **per rule**: one input that breaks only that rule and
satisfies all the others. (If an input breaks two rules at once, you cannot tell which rule the
function actually checks.) The checker has six buggy versions: wrong length limit in each
direction, and one version that forgets each of the other rules. Import with `from target import
is_valid_password`. Write at least 6 test functions.

**How this is checked.** Your `solution.py` is a file of pytest tests (chapter section 6). The
checker copies it next to the function above (saved as `target.py`) and runs real pytest, first on
the **correct** function (all your tests must pass), then on several **buggy copies** of it (at
least one of your tests must fail on each). Save the function as `target.py` in your folder
and run `python -m pytest solution.py` to try your tests yourself.
