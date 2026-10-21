## Approach

"Never crashes" is achieved by naming every **expected** failure, not by catching everything:

| Step | Failure | How it shows up |
|---|---|---|
| split | wrong number of parts | a length check |
| `float()` | not a number | `ValueError` |
| `float()` | `nan`, `inf` | no exception: `math.isfinite` |
| lookup operator | unknown | `in` check on the dispatch table |
| compute | zero divisor (`/ // %`, also `0 ** -1`) | `ZeroDivisionError` |
| compute | `**` too large | `OverflowError` |
| compute | `* + -` too large | no exception: the result is `inf` |
| compute | negative base, fractional power | no exception: a `complex` result |

Three of the failures raise nothing at all, which is why "wrap it in try" alone could never be
enough. The non-string argument is the caller's bug, so it raises `TypeError` instead of being
turned into a message.

## Code

```python
import math

OPERATIONS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
    "//": lambda a, b: a // b,
    "%": lambda a, b: a % b,
    "**": lambda a, b: a ** b,
}

TOO_LARGE = "Error: the result is too large"


def to_number(text):
    """Return float(text) if it is a finite number, else None."""
    try:
        value = float(text)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def calculate(expression):
    """Evaluate '<number> <operator> <number>'; return the result or an 'Error: ...' message."""
    if not isinstance(expression, str):
        raise TypeError(f"expression must be text (str), got {type(expression).__name__}")
    parts = expression.split()
    if len(parts) != 3:
        return "Error: write it as <number> <operator> <number>, for example 12 / 4"
    a_text, op, b_text = parts
    a = to_number(a_text)
    if a is None:
        return f"Error: {a_text!r} is not a number"
    b = to_number(b_text)
    if b is None:
        return f"Error: {b_text!r} is not a number"
    if op not in OPERATIONS:
        return f"Error: unknown operator {op!r}; use one of + - * / // % **"
    try:
        result = OPERATIONS[op](a, b)
    except ZeroDivisionError:
        return "Error: cannot divide by zero"
    except OverflowError:
        return TOO_LARGE
    if isinstance(result, complex):
        return "Error: the result is not a real number"
    if not math.isfinite(result):
        return TOO_LARGE
    return str(result)
```

## Complexity

O(n) in the length of the expression.

## Another way

An `if`/`elif` chain on the operator instead of the dispatch table works, but every new operator
then needs a new branch and the "unknown operator" message must be kept in sync by hand. The
table is also the single source for the operator list.
