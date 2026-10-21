## Hint 1

Change both `except Exception:` lines in `summarise` to the specific exceptions you expect and run
the first example again. Read the traceback you finally get.

## Hint 2

In `parse_result`, the bare `except` replaces **every** failure with one message. Which three
different things can go wrong with a line, and which of them raise by themselves (unpacking,
`int`) and which you raise yourself?

## Hint 3

- `parse_result`: split, check `len(parts) != 2` with an `if`, then `try` only `int(...)`, then the
  range `if`. No handler around the whole thing.
- `summarise`: `except ValueError as e: errors.append(f"line {number}: {e}")`, `else:` append the mark.
- The average: fix the typo, and catch only `ZeroDivisionError`.
