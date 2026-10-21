## Approach

The three bugs, and what was hiding each one:

1. **The typo `len(mark)`** raises `NameError` on every call. `except Exception` around the average
   turned it into `None`. Narrowing the handler to `ZeroDivisionError` (the only expected failure,
   for an empty list) makes the `NameError` visible at once, and the fix is obvious.
2. **`except Exception: pass` in the loop** threw away every error message, so `errors` stayed
   empty. Catch `ValueError` (what `parse_result` promises to raise) and record it.
3. **The wide `try` with a bare except in `parse_result`** caught the unpacking error, the
   `int` error, its own range error, and even an `AttributeError` for a non-string, and replaced
   them all with one message that is usually wrong. Narrow it: an `if` for the field count, a
   one-line `try` for `int`, an `if` for the range.

## Code

```python
def parse_result(line):
    """'name,marks' -> (name, marks). Raise ValueError saying what is wrong with a bad line."""
    parts = line.split(",")
    if len(parts) != 2:
        raise ValueError(f"expected 'name,marks', got {line!r}")
    name, marks_text = parts
    try:
        marks = int(marks_text)
    except ValueError:
        raise ValueError(f"marks must be a whole number, got {marks_text.strip()!r}") from None
    if marks < 0 or marks > 100:
        raise ValueError(f"marks must be from 0 to 100, got {marks}")
    return name.strip(), marks


def summarise(lines):
    """Return (average of valid marks or None, list of 'line N: message' for bad lines)."""
    marks = []
    errors = []
    for number, line in enumerate(lines, start=1):
        try:
            name, value = parse_result(line)
        except ValueError as e:
            errors.append(f"line {number}: {e}")
        else:
            marks.append(value)
    try:
        average = sum(marks) / len(marks)
    except ZeroDivisionError:
        average = None
    return average, errors
```

## Complexity

O(total length of the lines).

## Another way

The average could use LBYL, `average = sum(marks) / len(marks) if marks else None`, which is
equally clear. What matters is that no handler is wider than the failure it was written for. A
good habit when you inherit code like this: first replace every broad handler with a specific
one, run the tests, and let the tracebacks show you the hidden bugs.
