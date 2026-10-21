## Approach

The expression `float(a_text) / float(b_text)` is evaluated left to right: first `a_text` is
converted, then `b_text`, then the division. If either conversion fails, the division never
happens, so a non-number is reported before a zero. Two clauses give two different messages.

## Code

```python
def ratio(a_text, b_text):
    """Return a / b formatted with two decimals, or a message saying what to fix."""
    try:
        result = float(a_text) / float(b_text)
    except ValueError:
        return "Both values must be numbers, like 3 or 2.5."
    except ZeroDivisionError:
        return "The second value must not be zero."
    return f"{result:.2f}"
```

## Complexity

O(1) for normal-length input.

## Another way

Convert each value in its own `try` statement and name the box in the message ("The first value
must be a number"). That gives a more precise message at the cost of a few more lines, and is the
better design for a real form (section 13: narrow try blocks).
