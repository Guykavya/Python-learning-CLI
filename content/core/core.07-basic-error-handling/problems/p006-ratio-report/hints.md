## Hint 1

List the operations: two `float()` calls and one division. What does each raise when it fails?

## Hint 2

Both conversions fail with the same type, so one clause handles both. The division gets its own
clause. Format the result after the `try` statement (or in `else`).

## Hint 3

```
try:
    result = float(a_text) / float(b_text)
except ValueError:
    return numbers message
except ZeroDivisionError:
    return zero message
return f"{result:.2f}"
```
