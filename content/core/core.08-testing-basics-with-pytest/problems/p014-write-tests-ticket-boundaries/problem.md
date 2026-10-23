# Write tests: ticket_price boundaries

```python
def ticket_price(age):
    """Ticket price by age: 0-4 free, 5-12 child (50), 13-59 adult (100), 60 and over senior (60)."""
    if age < 0:
        raise ValueError("age cannot be negative")
    if age < 5:
        return 0
    if age < 13:
        return 50
    if age < 60:
        return 100
    return 60
```

Off-by-one bugs live at the **borders** between ranges. Write tests (`from target import
ticket_price`) that put a case on **both sides of every border**: the last age of one range and the
first age of the next. The checker has five buggy versions: some move a border by one year, one
accepts a negative age. Use `pytest.raises` for the error and write at least 5 test functions.

**How this is checked.** Your `solution.py` is a file of pytest tests (chapter section 6). The
checker copies it next to the function above (saved as `target.py`) and runs real pytest, first on
the **correct** function (all your tests must pass), then on several **buggy copies** of it (at
least one of your tests must fail on each). Save the function as `target.py` in your folder
and run `python -m pytest solution.py` to try your tests yourself.
